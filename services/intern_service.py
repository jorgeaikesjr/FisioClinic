from sqlalchemy.orm import Session
from models.intern import Intern
from schemas.intern import InternCreate, InternUpdate

def create_intern(db: Session, intern_data: InternCreate) -> Intern:
    db_intern = Intern(**intern_data.model_dump())
    db.add(db_intern)
    db.commit()
    db.refresh(db_intern)
    return db_intern

def get_intern(db: Session, intern_id: str) -> Intern | None:
    return db.query(Intern).filter(Intern.id == intern_id).first()

def get_interns(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> list[Intern]:
    query = db.query(Intern)
    if active_only:
        query = query.filter(Intern.is_active == True)
    return query.offset(skip).limit(limit).all()

def update_intern(db: Session, intern_id: str, intern_data: InternUpdate) -> Intern | None:
    db_intern = get_intern(db, intern_id)
    if db_intern:
        update_data = intern_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_intern, key, value)
        db.commit()
        db.refresh(db_intern)
    return db_intern

def delete_intern(db: Session, intern_id: str) -> Intern | None:
    """Deleção Lógica: Desativa o estagiário em vez de remover do banco."""
    db_intern = get_intern(db, intern_id)
    if db_intern:
        db_intern.is_active = False
        db.commit()
        db.refresh(db_intern)
    return db_intern
