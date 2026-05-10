from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.dependencies import get_db
from schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from services import patient_service

router = APIRouter()

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    return patient_service.create_patient(db=db, patient_data=patient)

@router.get("/", response_model=List[PatientResponse])
def read_patients(skip: int = 0, limit: int = 100, active_only: bool = False, db: Session = Depends(get_db)):
    return patient_service.get_patients(db=db, skip=skip, limit=limit, active_only=active_only)

@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(patient_id: str, db: Session = Depends(get_db)):
    db_patient = patient_service.get_patient(db=db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db_patient

@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: str, patient: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = patient_service.update_patient(db=db, patient_id=patient_id, patient_data=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db_patient

@router.get("/{patient_id}/future-count")
def read_patient_future_count(patient_id: str, db: Session = Depends(get_db)):
    from services import appointment_service
    return {"count": appointment_service.count_future_appointments(db, patient_id=patient_id)}

@router.delete("/{patient_id}", response_model=PatientResponse)
def delete_patient(patient_id: str, cancel_future: bool = False, db: Session = Depends(get_db)):
    if cancel_future:
        from services import appointment_service
        appointment_service.cancel_future_appointments(db, patient_id=patient_id)
    
    db_patient = patient_service.delete_patient(db=db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db_patient
