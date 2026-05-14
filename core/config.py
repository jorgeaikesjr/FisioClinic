from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    PROJECT_NAME: str = "FisioClinic Scheduler"
    DATABASE_URL: str = "sqlite:///./fisioclinic.db"
    
    # Define o tipo de clínica: "escola" ou "particular"
    CLINIC_TYPE: Literal["escola", "particular"] = "escola"
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
