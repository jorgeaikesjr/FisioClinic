import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class FittingList(Base):
    __tablename__ = "fitting_list"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    date_added = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento com paciente
    patient = relationship("Patient")
