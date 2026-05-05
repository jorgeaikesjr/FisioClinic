"""
test_patients.py — Testes de CRUD e regras de negócio para Pacientes.
"""


class TestCreatePatient:
    def test_create_minimal_ok(self, client, patient_payload):
        """Criação com campos obrigatórios deve retornar 201."""
        r = client.post("/api/v1/patients/", json=patient_payload)
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == patient_payload["name"]
        assert body["contact"] == patient_payload["contact"]
        assert body["is_active"] is True
        assert "id" in body

    def test_create_full_ok(self, client):
        """Criação com todos os campos opcionais deve funcionar."""
        payload = {
            "name": "João Completo",
            "contact": "11888880000",
            "guardian": "Ana Mãe",
            "anamnesis": "Dor lombar crônica",
            "is_active": True,
        }
        r = client.post("/api/v1/patients/", json=payload)
        assert r.status_code == 201
        body = r.json()
        assert body["guardian"] == "Ana Mãe"
        assert body["anamnesis"] == "Dor lombar crônica"

    def test_create_missing_name_returns_422(self, client):
        """Ausência do campo obrigatório 'name' deve retornar 422."""
        r = client.post("/api/v1/patients/", json={"contact": "11999990000"})
        assert r.status_code == 422

    def test_create_missing_contact_returns_422(self, client):
        """Ausência do campo obrigatório 'contact' deve retornar 422."""
        r = client.post("/api/v1/patients/", json={"name": "Teste"})
        assert r.status_code == 422

    def test_create_empty_body_returns_422(self, client):
        """Body vazio deve retornar 422."""
        r = client.post("/api/v1/patients/", json={})
        assert r.status_code == 422


class TestReadPatient:
    def test_list_empty(self, client):
        """Lista sem dados deve retornar array vazio."""
        r = client.get("/api/v1/patients/")
        assert r.status_code == 200
        assert r.json() == []

    def test_list_returns_created(self, client, created_patient):
        r = client.get("/api/v1/patients/")
        assert r.status_code == 200
        ids = [p["id"] for p in r.json()]
        assert created_patient["id"] in ids

    def test_get_by_id_ok(self, client, created_patient):
        pid = created_patient["id"]
        r = client.get(f"/api/v1/patients/{pid}")
        assert r.status_code == 200
        assert r.json()["id"] == pid

    def test_get_by_id_not_found(self, client):
        r = client.get("/api/v1/patients/nao-existe-000")
        assert r.status_code == 404

    def test_list_active_only_filter(self, client, created_patient):
        """Filtro active_only=true deve omitir pacientes inativos."""
        pid = created_patient["id"]
        # Inativa o paciente via DELETE (soft delete)
        client.delete(f"/api/v1/patients/{pid}")
        r = client.get("/api/v1/patients/?active_only=true")
        ids = [p["id"] for p in r.json()]
        assert pid not in ids

    def test_list_all_includes_inactive(self, client, created_patient):
        pid = created_patient["id"]
        client.delete(f"/api/v1/patients/{pid}")
        r = client.get("/api/v1/patients/")
        ids = [p["id"] for p in r.json()]
        assert pid in ids


class TestUpdatePatient:
    def test_update_name_ok(self, client, created_patient):
        pid = created_patient["id"]
        r = client.patch(f"/api/v1/patients/{pid}", json={"name": "Novo Nome"})
        assert r.status_code == 200
        assert r.json()["name"] == "Novo Nome"

    def test_update_contact_ok(self, client, created_patient):
        pid = created_patient["id"]
        r = client.patch(f"/api/v1/patients/{pid}", json={"contact": "21900000000"})
        assert r.status_code == 200
        assert r.json()["contact"] == "21900000000"

    def test_update_is_active_false(self, client, created_patient):
        pid = created_patient["id"]
        r = client.patch(f"/api/v1/patients/{pid}", json={"is_active": False})
        assert r.status_code == 200
        assert r.json()["is_active"] is False

    def test_update_not_found_returns_404(self, client):
        r = client.patch("/api/v1/patients/id-inexistente", json={"name": "X"})
        assert r.status_code == 404


class TestSoftDeletePatient:
    def test_delete_sets_inactive(self, client, created_patient):
        """DELETE deve inativar o paciente, não apagá-lo."""
        pid = created_patient["id"]
        r = client.delete(f"/api/v1/patients/{pid}")
        assert r.status_code == 200
        assert r.json()["is_active"] is False

    def test_delete_patient_still_retrievable(self, client, created_patient):
        pid = created_patient["id"]
        client.delete(f"/api/v1/patients/{pid}")
        r = client.get(f"/api/v1/patients/{pid}")
        assert r.status_code == 200        # ainda existe
        assert r.json()["is_active"] is False

    def test_delete_not_found_returns_404(self, client):
        r = client.delete("/api/v1/patients/id-inexistente")
        assert r.status_code == 404
