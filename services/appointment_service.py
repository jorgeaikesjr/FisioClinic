from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models.appointment import Appointment
from schemas.appointment import AppointmentCreate, AppointmentUpdate
from datetime import datetime

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

from services import patient_service

def create_appointment(db: Session, appointment_data: AppointmentCreate) -> Appointment:
    # 2. Validar que data_fim > data_inicio
    if appointment_data.start_time >= appointment_data.end_time:
        raise ValueError("A data/hora de término deve ser posterior à data/hora de início.")

    # 5. Validar se o paciente está ativo
    patient = patient_service.get_patient(db, appointment_data.patient_id)
    if patient and not patient.is_active:
        raise ValueError("Pacientes inativos não podem ser agendados.")

    # 1. Não permitir conflito de horário para o mesmo estagiário
    has_conflict = check_overlap(
        db, 
        appointment_data.intern_id, 
        appointment_data.start_time, 
        appointment_data.end_time
    )
    if has_conflict:
        raise ValueError("O estagiário já possui um agendamento neste horário.")

    # 3. Permitir múltiplos agendamentos por paciente (Sem restrição de conflito para paciente aqui)
    db_appointment = Appointment(**appointment_data.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointment(db: Session, appointment_id: str) -> Appointment | None:
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()

def get_appointments(db: Session, skip: int = 0, limit: int = 100) -> list[Appointment]:
    return db.query(Appointment).offset(skip).limit(limit).all()

def update_appointment(db: Session, appointment_id: str, appointment_data: AppointmentUpdate) -> Appointment | None:
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

    update_data = appointment_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
        
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: str, reason: str = "Cancelado pelo usuário") -> Appointment | None:
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
