from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.dependencies import get_db
from schemas.intern import InternCreate, InternUpdate, InternResponse
from services import intern_service

router = APIRouter()

@router.post("/", response_model=InternResponse, status_code=status.HTTP_201_CREATED)
def create_intern(intern: InternCreate, db: Session = Depends(get_db)):
    return intern_service.create_intern(db=db, intern_data=intern)

@router.get("/", response_model=List[InternResponse])
def read_interns(skip: int = 0, limit: int = 100, active_only: bool = False, db: Session = Depends(get_db)):
    return intern_service.get_interns(db=db, skip=skip, limit=limit, active_only=active_only)

@router.get("/{intern_id}", response_model=InternResponse)
def read_intern(intern_id: str, db: Session = Depends(get_db)):
    db_intern = intern_service.get_intern(db=db, intern_id=intern_id)
    if db_intern is None:
        raise HTTPException(status_code=404, detail="Estagiário não encontrado")
    return db_intern

@router.patch("/{intern_id}", response_model=InternResponse)
def update_intern(intern_id: str, intern: InternUpdate, db: Session = Depends(get_db)):
    db_intern = intern_service.update_intern(db=db, intern_id=intern_id, intern_data=intern)
    if db_intern is None:
        raise HTTPException(status_code=404, detail="Estagiário não encontrado")
    return db_intern

@router.get("/{intern_id}/future-count")
def read_intern_future_count(intern_id: str, db: Session = Depends(get_db)):
    from services import appointment_service
    return {"count": appointment_service.count_future_appointments(db, intern_id=intern_id)}

@router.delete("/{intern_id}", response_model=InternResponse)
def delete_intern(intern_id: str, cancel_future: bool = False, db: Session = Depends(get_db)):
    if cancel_future:
        from services import appointment_service
        appointment_service.cancel_future_appointments(db, intern_id=intern_id)
        
    # Retornamos o objeto com is_active=False para demonstrar a deleção lógica
    db_intern = intern_service.delete_intern(db=db, intern_id=intern_id)
    if db_intern is None:
        raise HTTPException(status_code=404, detail="Estagiário não encontrado")
    return db_intern
