from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.auth import require_auth
from models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})

@router.get("/change-password", response_class=HTMLResponse)
def change_password_page(request: Request):
    return templates.TemplateResponse(request=request, name="change_password.html", context={"request": request})

@router.get("/")
def read_root(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="calendar.html", context={"request": request, "current_user": current_user})

@router.get("/calendar")
def read_calendar(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="calendar.html", context={"request": request, "current_user": current_user})

@router.get("/patients")
def read_patients(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="patients.html", context={"request": request, "current_user": current_user})

@router.get("/interns", response_class=HTMLResponse)
async def interns_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="interns.html", context={"request": request, "current_user": current_user})

@router.get("/fitting-list", response_class=HTMLResponse)
async def fitting_list_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="fitting_list.html", context={"request": request, "current_user": current_user})

@router.get("/reports/absences", response_class=HTMLResponse)
async def reports_absences_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="reports_absences.html", context={"request": request, "current_user": current_user})

@router.get("/reports/weekly-summary", response_class=HTMLResponse)
async def reports_weekly_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="reports_weekly.html", context={"request": request, "current_user": current_user})

@router.get("/waiting-list", response_class=HTMLResponse)
async def waiting_list_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="waiting_list.html", context={"request": request, "current_user": current_user})

@router.get("/reports/waiting-list", response_class=HTMLResponse)
async def reports_waiting_list_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="reports_waiting_list.html", context={"request": request, "current_user": current_user})

@router.get("/reports/attendance", response_class=HTMLResponse)
async def reports_attendance_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="reports_attendance.html", context={"request": request, "current_user": current_user})

@router.get("/reports/patient-attendance", response_class=HTMLResponse)
async def reports_patient_attendance_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="reports_patient_attendance.html", context={"request": request, "current_user": current_user})

@router.get("/system-users", response_class=HTMLResponse)
async def system_users_page(request: Request, current_user: User = Depends(require_auth)):
    return templates.TemplateResponse(request=request, name="users.html", context={"request": request, "current_user": current_user})
