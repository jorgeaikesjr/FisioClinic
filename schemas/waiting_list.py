from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime
from schemas.patient import PatientResponse

CategoryType = Literal["Neuro Adulto", "Neuro Infantil", "Ortopedia"]

class WaitingListBase(BaseModel):
    patient_id: str = Field(..., description="ID do paciente (já cadastrado)")
    category: CategoryType = Field(..., description="Categoria da fila de espera")
    notes: Optional[str] = Field(None, description="Observações adicionais")

class WaitingListCreate(WaitingListBase):
    pass

class WaitingListResponse(WaitingListBase):
    id: str
    date_added: datetime
    patient: Optional[PatientResponse] = None

    model_config = ConfigDict(from_attributes=True)
