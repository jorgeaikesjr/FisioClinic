"""
test_interns.py — Testes de CRUD e regras de negócio para Estagiários.
"""


class TestCreateIntern:
    def test_create_ok(self, client, intern_payload):
        r = client.post("/api/v1/interns/", json=intern_payload)
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == intern_payload["name"]
        assert body["is_active"] is True
        assert "id" in body

    def test_create_inactive_intern(self, client):
        r = client.post("/api/v1/interns/", json={"name": "Inativo", "is_active": False})
        assert r.status_code == 201
        assert r.json()["is_active"] is False

    def test_create_missing_name_returns_422(self, client):
        r = client.post("/api/v1/interns/", json={"is_active": True})
        assert r.status_code == 422

    def test_create_empty_body_returns_422(self, client):
        r = client.post("/api/v1/interns/", json={})
        assert r.status_code == 422


class TestReadIntern:
    def test_list_empty(self, client):
        r = client.get("/api/v1/interns/")
        assert r.status_code == 200
        assert r.json() == []

    def test_list_returns_created(self, client, created_intern):
        r = client.get("/api/v1/interns/")
        ids = [i["id"] for i in r.json()]
        assert created_intern["id"] in ids

    def test_get_by_id_ok(self, client, created_intern):
        iid = created_intern["id"]
        r = client.get(f"/api/v1/interns/{iid}")
        assert r.status_code == 200
        assert r.json()["id"] == iid

    def test_get_by_id_not_found(self, client):
        r = client.get("/api/v1/interns/nao-existe")
        assert r.status_code == 404

    def test_list_active_only(self, client, created_intern):
        iid = created_intern["id"]
        client.delete(f"/api/v1/interns/{iid}")
        r = client.get("/api/v1/interns/?active_only=true")
        ids = [i["id"] for i in r.json()]
        assert iid not in ids


class TestUpdateIntern:
    def test_update_name_ok(self, client, created_intern):
        iid = created_intern["id"]
        r = client.patch(f"/api/v1/interns/{iid}", json={"name": "Novo Nome"})
        assert r.status_code == 200
        assert r.json()["name"] == "Novo Nome"

    def test_deactivate_via_patch(self, client, created_intern):
        iid = created_intern["id"]
        r = client.patch(f"/api/v1/interns/{iid}", json={"is_active": False})
        assert r.status_code == 200
        assert r.json()["is_active"] is False

    def test_update_not_found_returns_404(self, client):
        r = client.patch("/api/v1/interns/id-inexistente", json={"name": "X"})
        assert r.status_code == 404


class TestSoftDeleteIntern:
    def test_delete_sets_inactive(self, client, created_intern):
        iid = created_intern["id"]
        r = client.delete(f"/api/v1/interns/{iid}")
        assert r.status_code == 200
        assert r.json()["is_active"] is False

    def test_delete_intern_still_retrievable(self, client, created_intern):
        iid = created_intern["id"]
        client.delete(f"/api/v1/interns/{iid}")
        r = client.get(f"/api/v1/interns/{iid}")
        assert r.status_code == 200
        assert r.json()["is_active"] is False

    def test_delete_not_found_returns_404(self, client):
        r = client.delete("/api/v1/interns/id-inexistente")
        assert r.status_code == 404
