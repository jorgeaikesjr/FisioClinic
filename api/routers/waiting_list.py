from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from api.dependencies import get_db
from schemas.waiting_list import WaitingListCreate, WaitingListResponse
from services import waiting_list_service

router = APIRouter()

@router.post("/", response_model=WaitingListResponse, status_code=status.HTTP_201_CREATED)
def add_to_waiting_list(item: WaitingListCreate, db: Session = Depends(get_db)):
    # Adicionar validação se paciente existe se necessário,
    # porém o banco lançará erro de FK se não existir.
    return waiting_list_service.add_to_waiting_list(db=db, data=item)

@router.get("/", response_model=List[WaitingListResponse])
def get_waiting_list(category: Optional[str] = None, db: Session = Depends(get_db)):
    return waiting_list_service.get_waiting_list(db=db, category=category)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_waiting_list(item_id: str, db: Session = Depends(get_db)):
    db_item = waiting_list_service.remove_from_waiting_list(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado na fila de espera")
    return
