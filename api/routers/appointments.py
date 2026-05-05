from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.dependencies import get_db
from datetime import datetime
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse, CalendarEventResponse
from services import appointment_service

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return appointment_service.create_appointment(db=db, appointment_data=appointment)
    except ValueError as e:
        # Repassa os erros de regra de negócio (conflito ou datas inválidas) pro cliente com código 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[AppointmentResponse])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return appointment_service.get_appointments(db=db, skip=skip, limit=limit)

@router.get("/calendar", response_model=List[CalendarEventResponse])
def read_calendar_events(start: datetime, end: datetime, db: Session = Depends(get_db)):
    return appointment_service.get_calendar_events(db=db, start_date=start, end_date=end)

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def read_appointment(appointment_id: str, db: Session = Depends(get_db)):
    db_appointment = appointment_service.get_appointment(db=db, appointment_id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return db_appointment

@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: str, appointment: AppointmentUpdate, db: Session = Depends(get_db)):
    try:
        db_appointment = appointment_service.update_appointment(db=db, appointment_id=appointment_id, appointment_data=appointment)
        if db_appointment is None:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        return db_appointment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{appointment_id}", response_model=AppointmentResponse)
def delete_appointment(appointment_id: str, reason: str = "Cancelado pelo usuário", db: Session = Depends(get_db)):
    # Cancelamento que muda o status para "Cancelado"
    db_appointment = appointment_service.delete_appointment(db=db, appointment_id=appointment_id, reason=reason)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return db_appointment
