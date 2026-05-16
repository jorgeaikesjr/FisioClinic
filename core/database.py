from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
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
import models.user

# Configuração do engine
if not settings.DATABASE_URL:
    raise ValueError("A variável DATABASE_URL está vazia ou não foi configurada!")

connect_args = {}
engine_kwargs = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif settings.DATABASE_URL.startswith("postgresql"):
    # No Vercel (serverless) usando Supabase Pooler (PgBouncer porta 6543 em Transaction Mode),
    # é essencial usar NullPool para evitar que o SQLAlchemy retenha conexões inválidas/inconsistentes.
    engine_kwargs["poolclass"] = NullPool

print(f"Conectando ao banco de dados: {settings.DATABASE_URL.split('://')[0]}://...")

engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs
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
        
        # Migração manual simples para adicionar colunas em tabelas existentes
        from sqlalchemy import text
        with engine.begin() as conn:
            try:
                if settings.DATABASE_URL.startswith("postgresql"):
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
                else:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            except Exception:
                pass # Coluna já existe
                
            try:
                if settings.DATABASE_URL.startswith("postgresql"):
                    conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT TRUE"))
                else:
                    conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 1"))
            except Exception:
                pass # Coluna já existe
                
            # Força que o usuário 'admin' padrão seja admin (importante para bancos que foram migrados e ficaram com is_admin=False)
            try:
                if settings.DATABASE_URL.startswith("postgresql"):
                    conn.execute(text("UPDATE users SET is_admin = TRUE WHERE username = 'admin'"))
                else:
                    conn.execute(text("UPDATE users SET is_admin = 1 WHERE username = 'admin'"))
            except Exception as e:
                print(f"Erro ao atualizar privilégios do admin: {e}")

    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        # Em ambientes read-only (como Vercel) sem DATABASE_URL externa, 
        # isso pode falhar. Não travamos o app, mas logamos o erro.
