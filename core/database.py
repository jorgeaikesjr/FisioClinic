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
import models.waiting_list
import models.fitting_list

# Configuração do engine
# O parâmetro check_same_thread=False é necessário apenas para o SQLite.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args
)

# Criação da fábrica de sessões (SessionLocal)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Cria as tabelas no banco de dados SQLite caso elas não existam.
    Isso não apaga ou altera tabelas já existentes (seguro para inicialização local).
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        # Em ambientes read-only (como Vercel) sem DATABASE_URL externa, 
        # isso pode falhar. Não travamos o app, mas logamos o erro.
