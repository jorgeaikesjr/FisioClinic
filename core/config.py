from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    PROJECT_NAME: str = "FisioClinic Scheduler"
    DATABASE_URL: str = "sqlite:///./fisioclinic.db"
    
    # Define o tipo de clínica: "escola" ou "particular"
    CLINIC_TYPE: Literal["escola", "particular"] = "escola"
    
    # Segurança
    SECRET_KEY: str = "3f8e91a2b5c6d7e8f90a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

    def __init__(self, **values):
        import os
        from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
        
        # Prioridade para DATABASE_URL, depois variáveis automáticas do Vercel/Supabase
        db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("POSTGRES_PRISMA_URL")
        if db_url:
            values["DATABASE_URL"] = db_url
            
        super().__init__(**values)
        
        if self.DATABASE_URL:
            # 1. Limpa espaços e aspas
            self.DATABASE_URL = self.DATABASE_URL.strip().strip("'").strip('"')
            
            # 2. Corrige o prefixo (postgres -> postgresql)
            if self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
            
            # 3. Remove parâmetros inválidos (como 'supa' do Vercel) que travam o psycopg2
            try:
                u = urlparse(self.DATABASE_URL)
                query = parse_qsl(u.query)
                # Filtra apenas parâmetros conhecidos ou remove os explicitamente problemáticos
                query = [item for item in query if item[0] not in ['supa', 'pgbouncer']]
                new_query = urlencode(query)
                self.DATABASE_URL = urlunparse(u._replace(query=new_query))
            except Exception as e:
                print(f"Aviso: Erro ao limpar URL do banco: {e}")

settings = Settings()
