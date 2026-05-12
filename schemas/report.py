from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AbsenceReportItem(BaseModel):
    patient_id: str
    patient_name: str
    patient_contact: str
    absences_count: int
    justified_absences: int
    unjustified_absences: int

class WeeklySummaryItem(BaseModel):
    appointment_id: str
    patient_name: str
    start_time: datetime
    end_time: datetime
    status: str
    payment_method: Optional[str] = None
    amount_paid: Optional[float] = None

class AttendanceReport(BaseModel):
    total_count: int
    status_summary: dict[str, int]
    category_summary: dict[str, dict[str, int]] # Categoria -> { Status -> Count }
    
class PatientAttendanceReport(BaseModel):
    patient_name: str
    year: int
    monthly_counts: dict[int, int]
