import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from models.base import Base

class Appointment(Base):
    __tablename__ = "appointments"

    # UUID como chave primária
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Chaves Estrangeiras (mesmo tipo da PK)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    intern_id = Column(String(36), ForeignKey("interns.id"), nullable=False, index=True)
    
    # Campos obrigatórios de agendamento
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="Agendado", nullable=False) # Agendado, Cancelado, Realizado
    
    # Campos opcionais
    cancel_reason = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)  # Pix, Dinheiro, Cartão de Crédito, Cartão de Débito, Transferência
    amount_paid = Column(Float, nullable=True)

    # Relacionamentos bidirecionais
    patient = relationship("Patient", back_populates="appointments")
    intern = relationship("Intern", back_populates="appointments")
