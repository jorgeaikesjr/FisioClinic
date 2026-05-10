from typing import Optional
from sqlalchemy.orm import Session, joinedload
from models.fitting_list import FittingList
from schemas.fitting_list import FittingListCreate

def get_fitting_list(db: Session) -> list[FittingList]:
    return db.query(FittingList).options(joinedload(FittingList.patient)).order_by(FittingList.date_added.asc()).all()

def add_to_fitting_list(db: Session, data: FittingListCreate) -> FittingList:
    # Evitar duplicados na lista de encaixe (opcional, mas recomendado)
    existing = db.query(FittingList).filter(FittingList.patient_id == data.patient_id).first()
    if existing:
        return existing
        
    db_item = FittingList(**data.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def remove_from_fitting_list(db: Session, item_id: str) -> bool:
    db_item = db.query(FittingList).filter(FittingList.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False
