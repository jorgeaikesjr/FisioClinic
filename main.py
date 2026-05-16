from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.config import settings

from contextlib import asynccontextmanager
from core.database import init_db, SessionLocal
from core.auth import NotAuthenticatedException, MustChangePasswordException
from core.security import get_password_hash
from models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o banco de dados antes de a aplicação aceitar requisições
    init_db()
    
    # Cria usuário admin padrão se não houver usuários
    try:
        db = SessionLocal()
        if db.query(User).count() == 0:
            print("Criando usuário admin padrão...")
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                must_change_password=False
            )
            db.add(admin_user)
            db.commit()
    except Exception as e:
        print(f"Erro ao criar usuário admin: {e}")
    finally:
        db.close()
        
    yield

# Inicialização do FastAPI
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.state.settings = settings

@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_exception_handler(request: Request, exc: NotAuthenticatedException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Não autorizado"},
        )
    return RedirectResponse(url="/login")

@app.exception_handler(MustChangePasswordException)
async def must_change_password_exception_handler(request: Request, exc: MustChangePasswordException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Troca de senha obrigatória exigida"},
        )
    return RedirectResponse(url="/change-password")

# Montar arquivos estáticos e templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Rotas - inclua aqui os routers da API
from api.routers import patients, interns, appointments, views, reports, settings as settings_router, waiting_list, fitting_list, auth, users

from fastapi import Depends
from core.auth import require_auth

app.include_router(views.router)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"], dependencies=[Depends(require_auth)])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Pacientes"], dependencies=[Depends(require_auth)])
app.include_router(interns.router, prefix="/api/v1/interns", tags=["Estagiários"], dependencies=[Depends(require_auth)])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Agendamentos"], dependencies=[Depends(require_auth)])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"], dependencies=[Depends(require_auth)])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"], dependencies=[Depends(require_auth)])
app.include_router(waiting_list.router, prefix="/api/v1/waiting-list", tags=["Fila de Espera"], dependencies=[Depends(require_auth)])
app.include_router(fitting_list.router, prefix="/api/v1/fitting-list", tags=["Lista de Encaixe"], dependencies=[Depends(require_auth)])
