from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def read_root(request: Request):
    # Redireciona a raiz para o calendário
    return templates.TemplateResponse(request=request, name="calendar.html", context={"request": request})

@router.get("/calendar")
def read_calendar(request: Request):
    return templates.TemplateResponse(request=request, name="calendar.html", context={"request": request})

@router.get("/patients")
def read_patients(request: Request):
    return templates.TemplateResponse(request=request, name="patients.html", context={"request": request})

@router.get("/interns", response_class=HTMLResponse)
async def interns_page(request: Request):
    return templates.TemplateResponse(request=request, name="interns.html", context={"request": request})

@router.get("/fitting-list", response_class=HTMLResponse)
async def fitting_list_page(request: Request):
    return templates.TemplateResponse(request=request, name="fitting_list.html", context={"request": request})

@router.get("/reports/absences", response_class=HTMLResponse)
async def reports_absences_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports_absences.html", context={"request": request})

@router.get("/reports/weekly-summary", response_class=HTMLResponse)
async def reports_weekly_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports_weekly.html", context={"request": request})

@router.get("/waiting-list", response_class=HTMLResponse)
async def waiting_list_page(request: Request):
    return templates.TemplateResponse(request=request, name="waiting_list.html", context={"request": request})

@router.get("/reports/waiting-list", response_class=HTMLResponse)
async def reports_waiting_list_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports_waiting_list.html", context={"request": request})

@router.get("/reports/attendance", response_class=HTMLResponse)
async def reports_attendance_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports_attendance.html", context={"request": request})

@router.get("/reports/patient-attendance", response_class=HTMLResponse)
async def reports_patient_attendance_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports_patient_attendance.html", context={"request": request})
