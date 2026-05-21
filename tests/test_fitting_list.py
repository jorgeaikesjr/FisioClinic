"""
test_fitting_list.py — Testes para as rotas de lista de encaixe.
"""

def test_add_to_fitting_list_success(client, created_patient):
    response = client.post("/api/v1/fitting-list/", json={
        "patient_id": created_patient["id"]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == created_patient["id"]
    assert "id" in data
    assert "date_added" in data


def test_add_to_fitting_list_duplicate(client, created_patient):
    # Tenta adicionar o mesmo paciente duas vezes
    # O serviço retorna a mesma entrada existente em vez de criar duplicado
    r1 = client.post("/api/v1/fitting-list/", json={
        "patient_id": created_patient["id"]
    })
    assert r1.status_code == 201
    id1 = r1.json()["id"]

    r2 = client.post("/api/v1/fitting-list/", json={
        "patient_id": created_patient["id"]
    })
    # Deve retornar a entrada existente
    assert r2.status_code == 201
    assert r2.json()["id"] == id1

    # Verifica que a lista possui apenas 1 item
    r_list = client.get("/api/v1/fitting-list/")
    assert len(r_list.json()) == 1


def test_get_fitting_list(client, created_patient):
    r_add = client.post("/api/v1/fitting-list/", json={
        "patient_id": created_patient["id"]
    })
    item_id = r_add.json()["id"]

    response = client.get("/api/v1/fitting-list/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    ids = [i["id"] for i in items]
    assert item_id in ids


def test_remove_from_fitting_list_success(client, created_patient):
    r_add = client.post("/api/v1/fitting-list/", json={
        "patient_id": created_patient["id"]
    })
    item_id = r_add.json()["id"]

    # Remove
    r_del = client.delete(f"/api/v1/fitting-list/{item_id}")
    assert r_del.status_code == 200
    assert r_del.json() == {"detail": "Removido com sucesso"}

    # Verifica se saiu
    r_list = client.get("/api/v1/fitting-list/")
    ids = [i["id"] for i in r_list.json()]
    assert item_id not in ids


def test_remove_from_fitting_list_not_found(client):
    response = client.delete("/api/v1/fitting-list/id_inexistente")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()
