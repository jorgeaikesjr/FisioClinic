from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FisioClinic Scheduler"
    DATABASE_URL: str = "sqlite:///./fisioclinic.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
