from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from schemas.patient import PatientResponse

class FittingListBase(BaseModel):
    patient_id: str

class FittingListCreate(FittingListBase):
    pass

class FittingListResponse(BaseModel):
    id: str
    patient_id: str
    date_added: datetime
    patient: Optional[PatientResponse] = None

    model_config = ConfigDict(from_attributes=True)
