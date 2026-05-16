from fastapi import Request, Depends, HTTPException, status
import jwt
from sqlalchemy.orm import Session
from core.config import settings
from core.database import SessionLocal
from core.security import ALGORITHM
from models.user import User

class NotAuthenticatedException(Exception):
    pass

class MustChangePasswordException(Exception):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise NotAuthenticatedException()
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise NotAuthenticatedException()
    except jwt.PyJWTError:
        raise NotAuthenticatedException()
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise NotAuthenticatedException()
    return user

def require_auth(request: Request, user: User = Depends(get_current_user)):
    # Se a rota acessada for a de trocar a senha ou de fazer logout ou obter o status inicial do app, deixa passar
    if request.url.path in ["/change-password", "/api/v1/auth/change-password", "/api/v1/auth/logout", "/api/v1/settings/clinic-type"]:
        return user
    
    # Se o usuário precisa trocar a senha e a rota não é uma das permitidas acima
    if user.must_change_password:
        raise MustChangePasswordException()
        
    return user

def require_admin(user: User = Depends(require_auth)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer privilégios de administrador."
        )
    return user
