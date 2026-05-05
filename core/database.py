from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Importação da base declarativa
from models.base import Base

# Importação de todos os modelos é obrigatória aqui ANTES de rodar o create_all(),
# para que o SQLAlchemy saiba quais tabelas precisam ser criadas.
import models.patient
import models.intern
import models.appointment

# Configuração do engine do SQLite
# O parâmetro check_same_thread=False é necessário apenas para o SQLite no FastAPI.
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

# Criação da fábrica de sessões (SessionLocal)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Cria as tabelas no banco de dados SQLite caso elas não existam.
    Isso não apaga ou altera tabelas já existentes (seguro para inicialização local).
    """
    Base.metadata.create_all(bind=engine)
