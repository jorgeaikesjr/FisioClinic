from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def read_root(request: Request):
    # Redireciona a raiz para o calendário
    return templates.TemplateResponse("calendar.html", {"request": request})

@router.get("/calendar")
def read_calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})

@router.get("/patients")
def read_patients(request: Request):
    return templates.TemplateResponse("patients.html", {"request": request})

@router.get("/interns", response_class=HTMLResponse)
async def interns_page(request: Request):
    return templates.TemplateResponse("interns.html", {"request": request})

@router.get("/reports/absences", response_class=HTMLResponse)
async def reports_absences_page(request: Request):
    return templates.TemplateResponse("reports_absences.html", {"request": request})

@router.get("/reports/weekly-summary", response_class=HTMLResponse)
async def reports_weekly_page(request: Request):
    return templates.TemplateResponse("reports_weekly.html", {"request": request})
