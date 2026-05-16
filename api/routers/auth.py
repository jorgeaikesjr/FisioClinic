from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import SessionLocal
from core.security import verify_password, create_access_token
from models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    # Define o cookie HTTP Only
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60, # 7 dias
        expires=7 * 24 * 60 * 60,
        samesite="lax",
        secure=False, # Como não temos HTTPS local garantido, manter False. Em prod no Vercel (HTTPS), o browser aceita.
    )
    return {"message": "Login realizado com sucesso"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout realizado com sucesso"}
