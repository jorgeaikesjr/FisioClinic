from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from core.database import SessionLocal
from core.auth import require_admin
from core.security import get_password_hash
from models.user import User
from api.dependencies import get_db

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class UserResponse(BaseModel):
    id: str
    username: str
    is_admin: bool
    must_change_password: bool

    class Config:
        orm_mode = True

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    users = db.query(User).all()
    return users

@router.post("/", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe no sistema"
        )
    
    new_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_admin=user_in.is_admin,
        must_change_password=True  # Sempre força troca no primeiro login
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user_to_delete.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir a si mesmo")
        
    db.delete(user_to_delete)
    db.commit()
    return None
