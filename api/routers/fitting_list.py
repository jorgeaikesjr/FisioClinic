from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.dependencies import get_db
from schemas.fitting_list import FittingListCreate, FittingListResponse
from services import fitting_list_service

router = APIRouter()

@router.get("/", response_model=List[FittingListResponse])
def read_fitting_list(db: Session = Depends(get_db)):
    return fitting_list_service.get_fitting_list(db)

@router.post("/", response_model=FittingListResponse, status_code=status.HTTP_201_CREATED)
def add_patient(data: FittingListCreate, db: Session = Depends(get_db)):
    return fitting_list_service.add_to_fitting_list(db, data)

@router.delete("/{item_id}")
def remove_patient(item_id: str, db: Session = Depends(get_db)):
    success = fitting_list_service.remove_from_fitting_list(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item não encontrado na lista de encaixe")
    return {"detail": "Removido com sucesso"}
