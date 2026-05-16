from fastapi import Request, Depends, HTTPException, status
import jwt
from sqlalchemy.orm import Session
from core.config import settings
from core.database import SessionLocal
from core.security import ALGORITHM
from models.user import User

class NotAuthenticatedException(Exception):
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

def require_auth(user: User = Depends(get_current_user)):
    return user
