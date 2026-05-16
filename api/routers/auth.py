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

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/login")
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    # Garante que o usuário admin exista (especialmente importante no Vercel onde o lifespan pode não rodar)
    if db.query(User).count() == 0:
        from core.security import get_password_hash
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            must_change_password=False
        )
        db.add(admin_user)
        db.commit()

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
    return {
        "message": "Login realizado com sucesso",
        "must_change_password": user.must_change_password
    }

@router.post("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from core.security import get_password_hash
    
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
        
    current_user.hashed_password = get_password_hash(data.new_password)
    current_user.must_change_password = False
    db.commit()
    
    return {"message": "Senha atualizada com sucesso"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout realizado com sucesso"}
