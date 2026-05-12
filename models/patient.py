import uuid
from sqlalchemy import Column, String, Text, Boolean, Date
from sqlalchemy.orm import relationship
from models.base import Base

class Patient(Base):
    __tablename__ = "patients"

    # UUID como chave primária
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Campos obrigatórios
    name = Column(String, nullable=False, index=True)
    contact = Column(String, nullable=False)
    
    # Campos opcionais
    guardian = Column(String, nullable=True)
    sex = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    anamnesis = Column(Text, nullable=True)
    
    # Controle de status (Soft Delete)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
