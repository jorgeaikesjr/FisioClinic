"""
conftest.py — Fixtures compartilhadas para todos os testes.

Estratégia:
  - Usa um arquivo SQLite temporário isolado (não o fisioclinic.db de produção).
  - O arquivo é criado antes de cada teste e apagado após, garantindo isolamento.
  - db_module.SessionLocal e db_module.engine são substituídos diretamente,
    pois api/dependencies.py faz lookup dinâmico em tempo de execução.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
import models.patient      # noqa: F401
import models.intern       # noqa: F401
import models.appointment  # noqa: F401

import core.database as db_module

TEST_DB_PATH = "test_fisioclinic.db"
TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_PATH}"


@pytest.fixture(autouse=True)
def setup_database():
    """Cria banco de dados de teste antes de cada teste e remove após."""
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Injeta no módulo — get_db() faz lookup dinâmico
    db_module.engine = engine
    db_module.SessionLocal = TestingSessionLocal

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    # Remove o arquivo de banco de testes
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture()
def client():
    from main import app
    with TestClient(app) as c:
        yield c


# ── Payloads e entidades básicas ──────────────────────────────────────────────

@pytest.fixture()
def patient_payload():
    return {"name": "Maria Silva", "contact": "11999990000"}


@pytest.fixture()
def intern_payload():
    return {"name": "Dr. Carlos", "is_active": True}


@pytest.fixture()
def created_patient(client, patient_payload):
    r = client.post("/api/v1/patients/", json=patient_payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def created_intern(client, intern_payload):
    r = client.post("/api/v1/interns/", json=intern_payload)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def appointment_payload(created_patient, created_intern):
    return {
        "patient_id": created_patient["id"],
        "intern_id":  created_intern["id"],
        "start_time": "2026-06-10T09:00:00",
        "end_time":   "2026-06-10T09:50:00",
    }


@pytest.fixture()
def created_appointment(client, appointment_payload):
    r = client.post("/api/v1/appointments/", json=appointment_payload)
    assert r.status_code == 201, r.text
    return r.json()
