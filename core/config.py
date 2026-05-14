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

    def __init__(self, **values):
        super().__init__(**values)
        # Limpa espaços e aspas que podem vir do ambiente (Vercel/Docker)
        if self.DATABASE_URL:
            self.DATABASE_URL = self.DATABASE_URL.strip().strip("'").strip('"')
            
            # Corrige o prefixo do Supabase/Postgres
            if self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

settings = Settings()
