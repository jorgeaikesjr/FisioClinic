import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from models.base import Base

class Intern(Base):
    __tablename__ = "interns"

    # UUID como chave primária
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Campos obrigatórios
    name = Column(String, nullable=False, index=True)
    contact = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    appointments = relationship("Appointment", back_populates="intern", cascade="all, delete-orphan")
