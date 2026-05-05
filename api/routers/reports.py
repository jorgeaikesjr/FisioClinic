from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.dependencies import get_db
from schemas.report import AbsenceReportItem
from services import report_service

router = APIRouter()

@router.get("/absences", response_model=List[AbsenceReportItem])
def read_absences_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    return report_service.get_absences_report(db=db, start_date=start_date, end_date=end_date)
