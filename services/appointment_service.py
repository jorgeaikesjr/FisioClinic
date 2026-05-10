from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models.appointment import Appointment
from schemas.appointment import AppointmentCreate, AppointmentUpdate
from datetime import datetime, timedelta

def check_overlap(db: Session, intern_id: str, start_time: datetime, end_time: datetime, exclude_appointment_id: str = None):
    query = db.query(Appointment).filter(
        Appointment.intern_id == intern_id,
        Appointment.status != "Cancelado",
        # Um conflito ocorre se o agendamento existente começar antes do novo terminar
        # e terminar depois que o novo começar.
        Appointment.start_time < end_time,
        Appointment.end_time > start_time
    )
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
        
    return query.first() is not None

from services import patient_service, intern_service

def create_appointment(db: Session, appointment_data: AppointmentCreate) -> list[Appointment]:
    # 2. Validar que data_fim > data_inicio
    if appointment_data.start_time >= appointment_data.end_time:
        raise ValueError("A data/hora de término deve ser posterior à data/hora de início.")

    patient = patient_service.get_patient(db, appointment_data.patient_id)
    if patient and not patient.is_active:
        raise ValueError(f"O paciente '{patient.name}' está inativo e não pode receber novos agendamentos.")

    # Validar se o estagiário está ativo
    intern = intern_service.get_intern(db, appointment_data.intern_id)
    if intern and not intern.is_active:
        raise ValueError(f"O estagiário '{intern.name}' está inativo e não pode receber novos agendamentos.")

    appointments_to_create = []

    if appointment_data.recurrence_weeks and appointment_data.recurrence_days:
        base_start = appointment_data.start_time
        base_end = appointment_data.end_time
        duration = base_end - base_start
        current_date = base_start.date()

        for week in range(appointment_data.recurrence_weeks):
            for day_idx in appointment_data.recurrence_days:
                days_to_add = day_idx - current_date.weekday() + (week * 7)
                target_date = current_date + timedelta(days=days_to_add)

                if target_date < current_date:
                    continue

                target_start = datetime.combine(target_date, base_start.time())
                target_end = target_start + duration

                # 1. Não permitir conflito de horário
                has_conflict = check_overlap(
                    db, 
                    appointment_data.intern_id, 
                    target_start, 
                    target_end
                )
                if has_conflict:
                    raise ValueError(f"Conflito de horário detectado no dia {target_start.strftime('%d/%m/%Y às %H:%M')}.")

                app_data_dict = appointment_data.model_dump(exclude={"recurrence_days", "recurrence_weeks"})
                app_data_dict["start_time"] = target_start
                app_data_dict["end_time"] = target_end
                appointments_to_create.append(Appointment(**app_data_dict))
    else:
        # Agendamento único
        has_conflict = check_overlap(
            db, 
            appointment_data.intern_id, 
            appointment_data.start_time, 
            appointment_data.end_time
        )
        if has_conflict:
            raise ValueError("O estagiário já possui um agendamento neste horário.")

        app_data_dict = appointment_data.model_dump(exclude={"recurrence_days", "recurrence_weeks"})
        appointments_to_create.append(Appointment(**app_data_dict))

    # 3. Permitir múltiplos agendamentos por paciente
    db.add_all(appointments_to_create)
    db.commit()
    for appt in appointments_to_create:
        db.refresh(appt)
        
    return appointments_to_create

def get_appointment(db: Session, appointment_id: str) -> Optional[Appointment]:
    return db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.intern)
    ).filter(Appointment.id == appointment_id).first()

def get_appointments(db: Session, skip: int = 0, limit: int = 100) -> list[Appointment]:
    return db.query(Appointment).offset(skip).limit(limit).all()

def update_appointment(db: Session, appointment_id: str, appointment_data: AppointmentUpdate) -> Optional[Appointment]:
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None

    # Obter os horários futuros, usando os novos dados se fornecidos, senão manter os atuais
    new_start = appointment_data.start_time if appointment_data.start_time else db_appointment.start_time
    new_end = appointment_data.end_time if appointment_data.end_time else db_appointment.end_time
    new_intern_id = db_appointment.intern_id # Estagiário não muda pelo schema base, se mudar, usar o novo

    # Revalidar lógica de tempo se as datas sofreram alteração
    if appointment_data.start_time or appointment_data.end_time:
        if new_start >= new_end:
            raise ValueError("A data/hora de término deve ser posterior à data/hora de início.")
            
        has_conflict = check_overlap(
            db, 
            new_intern_id, 
            new_start, 
            new_end, 
            exclude_appointment_id=appointment_id
        )
        if has_conflict:
            raise ValueError("O estagiário já possui outro agendamento neste horário.")

        # Validar se o estagiário está ativo APENAS se estiver sendo alterado
        if appointment_data.intern_id and appointment_data.intern_id != db_appointment.intern_id:
            intern = intern_service.get_intern(db, appointment_data.intern_id)
            if intern and not intern.is_active:
                raise ValueError(f"Não é possível transferir agendamentos para o estagiário '{intern.name}' pois ele está inativo.")

        # Validar paciente se alterado
        if appointment_data.patient_id and appointment_data.patient_id != db_appointment.patient_id:
            patient = patient_service.get_patient(db, appointment_data.patient_id)
            if patient and not patient.is_active:
                raise ValueError(f"Não é possível transferir agendamentos para o paciente '{patient.name}' pois ele está inativo.")

    update_data = appointment_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
        
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: str, reason: str = "Cancelado pelo usuário") -> Optional[Appointment]:
    # 4. Cancelamento deve apenas alterar status (Deleção Lógica)
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment:
        db_appointment.status = "Cancelado"
        db_appointment.cancel_reason = reason
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

from sqlalchemy.orm import joinedload

def get_calendar_events(db: Session, start_date: datetime, end_date: datetime) -> list[dict]:
    # Buscar agendamentos no período, fazendo um JOIN automático para trazer Paciente e Estagiário
    appointments = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.intern)
    ).filter(
        Appointment.start_time < end_date,
        Appointment.end_time > start_date
    ).all()
    
    events = []
    for appt in appointments:
        patient_name = appt.patient.name if appt.patient else "Desconhecido"
        intern_name = appt.intern.name if appt.intern else "Desconhecido"
        
        events.append({
            "id": appt.id,
            "title": f"{patient_name} - {intern_name}",
            "start": appt.start_time,
            "end": appt.end_time,
            "status": appt.status
        })
    return events

def count_future_appointments(db: Session, patient_id: str = None, intern_id: str = None) -> int:
    """Conta agendamentos futuros não cancelados."""
    now = datetime.now()
    query = db.query(Appointment).filter(
        Appointment.start_time > now,
        Appointment.status != "Cancelado"
    )
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if intern_id:
        query = query.filter(Appointment.intern_id == intern_id)
    
    return query.count()

def cancel_future_appointments(db: Session, patient_id: str = None, intern_id: str = None):
    """Cancela em lote agendamentos futuros."""
    now = datetime.now()
    query = db.query(Appointment).filter(
        Appointment.start_time > now,
        Appointment.status != "Cancelado"
    )
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if intern_id:
        query = query.filter(Appointment.intern_id == intern_id)
    
    future_appts = query.all()
    for appt in future_appts:
        appt.status = "Cancelado"
        appt.cancel_reason = "Cancelado automaticamente por inativação do registro vinculado."
    
    db.commit()
