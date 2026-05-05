import core.database as db_module


def get_db():
    # Busca SessionLocal em tempo de execução para que os testes possam substituí-lo
    db = db_module.SessionLocal()
    try:
        yield db
    finally:
        db.close()
