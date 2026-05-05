from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from models.appointment import Appointment
from models.patient import Patient
from schemas.report import AbsenceReportItem, WeeklySummaryItem

def get_absences_report(db: Session, start_date: datetime | None = None, end_date: datetime | None = None) -> list[AbsenceReportItem]:
    query = db.query(
        Patient.id.label("patient_id"),
        Patient.name.label("patient_name"),
        Patient.contact.label("patient_contact"),
        func.count(Appointment.id).label("absences_count")
    ).join(Appointment, Patient.id == Appointment.patient_id) \
     .filter(Appointment.status == "Faltou")
     
    if start_date:
        query = query.filter(Appointment.start_time >= start_date)
    if end_date:
        query = query.filter(Appointment.start_time <= end_date)
        
    query = query.group_by(Patient.id).order_by(func.count(Appointment.id).desc())
    
    results = query.all()
    
    report = []
    for row in results:
        report.append(AbsenceReportItem(
            patient_id=str(row.patient_id),
            patient_name=row.patient_name,
            patient_contact=row.patient_contact,
            absences_count=row.absences_count
        ))
        
    return report


def get_weekly_summary(db: Session, start_date: datetime, end_date: datetime) -> list[WeeklySummaryItem]:
    """Retorna todos os agendamentos (exceto cancelados) no período, ordenados por data/hora."""
    appointments = (
        db.query(Appointment, Patient.name.label("patient_name"))
        .join(Patient, Patient.id == Appointment.patient_id)
        .filter(
            Appointment.start_time >= start_date,
            Appointment.start_time <= end_date,
            Appointment.status != "Cancelado"
        )
        .order_by(Appointment.start_time)
        .all()
    )

    return [
        WeeklySummaryItem(
            appointment_id=appt.id,
            patient_name=patient_name,
            start_time=appt.start_time,
            end_time=appt.end_time,
            status=appt.status,
            payment_method=appt.payment_method,
            amount_paid=appt.amount_paid,
        )
        for appt, patient_name in appointments
    ]
