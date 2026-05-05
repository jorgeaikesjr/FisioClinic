from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.config import settings

from contextlib import asynccontextmanager
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o banco de dados antes de a aplicação aceitar requisições
    init_db()
    yield

# Inicialização do FastAPI
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Montar arquivos estáticos e templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Rotas - inclua aqui os routers da API
from api.routers import patients, interns, appointments, views, reports

app.include_router(views.router)
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Pacientes"])
app.include_router(interns.router, prefix="/api/v1/interns", tags=["Estagiários"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Agendamentos"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
