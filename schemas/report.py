from pydantic import BaseModel
from typing import Optional

class AbsenceReportItem(BaseModel):
    patient_id: str
    patient_name: str
    patient_contact: str
    absences_count: int
