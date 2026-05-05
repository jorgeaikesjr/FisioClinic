from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    PROJECT_NAME: str = "FisioClinic Scheduler"
    DATABASE_URL: str = "sqlite:///./fisioclinic.db"
    
    # Define o tipo de clínica: "escola" ou "particular"
    # Para alterar, edite o arquivo .env na raiz do projeto
    CLINIC_TYPE: Literal["escola", "particular"] = "escola"
    
    class Config:
        env_file = ".env"

settings = Settings()
