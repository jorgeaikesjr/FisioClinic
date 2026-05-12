from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.dependencies import get_db
from schemas.report import AbsenceReportItem, WeeklySummaryItem, AttendanceReport, PatientAttendanceReport
from services import report_service

router = APIRouter()

@router.get("/absences", response_model=List[AbsenceReportItem])
def read_absences_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    return report_service.get_absences_report(db=db, start_date=start_date, end_date=end_date)


@router.get("/weekly-summary", response_model=List[WeeklySummaryItem])
def read_weekly_summary(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    return report_service.get_weekly_summary(db=db, start_date=start_date, end_date=end_date)


@router.get("/attendance", response_model=AttendanceReport)
def read_attendance_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    return report_service.get_attendance_report(db=db, start_date=start_date, end_date=end_date)


@router.get("/patient-attendance", response_model=PatientAttendanceReport)
def read_patient_attendance_report(
    patient_id: str,
    year: int,
    db: Session = Depends(get_db)
):
    return report_service.get_patient_attendance_report(db=db, patient_id=patient_id, year=year)
