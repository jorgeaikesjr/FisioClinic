"""
test_settings.py — Testes para as rotas de configurações.
"""
from core.config import settings

def test_get_clinic_type(client):
    response = client.get("/api/v1/settings/clinic-type")
    assert response.status_code == 200
    data = response.json()
    assert "clinic_type" in data
    assert data["clinic_type"] == settings.CLINIC_TYPE
