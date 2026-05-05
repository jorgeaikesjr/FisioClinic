from sqlalchemy.orm import Session
from models.patient import Patient
from schemas.patient import PatientCreate, PatientUpdate

def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    # Usando model_dump para o Pydantic v2
    db_patient = Patient(**patient_data.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patient(db: Session, patient_id: str) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> list[Patient]:
    query = db.query(Patient)
    if active_only:
        query = query.filter(Patient.is_active == True)
    return query.offset(skip).limit(limit).all()

def update_patient(db: Session, patient_id: str, patient_data: PatientUpdate) -> Patient | None:
    db_patient = get_patient(db, patient_id)
    if db_patient:
        # exclude_unset garante que só atualizaremos campos explicitamente enviados
        update_data = patient_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_patient, key, value)
        db.commit()
        db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: str) -> Patient | None:
    """Deleção lógica: Desativa o paciente para manter o histórico."""
    db_patient = get_patient(db, patient_id)
    if db_patient:
        db_patient.is_active = False
        db.commit()
        db.refresh(db_patient)
    return db_patient
