"""
test_waiting_list.py — Testes para as rotas de fila de espera.
"""

def test_add_to_waiting_list_success(client, created_patient):
    response = client.post("/api/v1/waiting-list/", json={
        "patient_id": created_patient["id"],
        "category": "Neuro Adulto",
        "notes": "Paciente precisa de horário vespertino"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == created_patient["id"]
    assert data["category"] == "Neuro Adulto"
    assert data["notes"] == "Paciente precisa de horário vespertino"
    assert "id" in data
    assert "date_added" in data


def test_add_to_waiting_list_invalid_category(client, created_patient):
    # Categoria deve ser uma das Literal permitidas: "Neuro Adulto", "Neuro Infantil", "Ortopedia", "Cardio", "Saúde Coletiva"
    response = client.post("/api/v1/waiting-list/", json={
        "patient_id": created_patient["id"],
        "category": "Categoria Invalida",
    })
    assert response.status_code == 422


def test_get_waiting_list(client, created_patient):
    # Adiciona paciente na fila
    r_add = client.post("/api/v1/waiting-list/", json={
        "patient_id": created_patient["id"],
        "category": "Ortopedia",
        "notes": "Obs Ortopedia"
    })
    item_id = r_add.json()["id"]

    # Busca lista sem filtro
    r_list = client.get("/api/v1/waiting-list/")
    assert r_list.status_code == 200
    items = r_list.json()
    assert len(items) >= 1
    ids = [i["id"] for i in items]
    assert item_id in ids


def test_get_waiting_list_filter(client, created_patient):
    # Adiciona dois pacientes em categorias diferentes
    r_patient2 = client.post("/api/v1/patients/", json={"name": "Paciente Do waiting", "contact": "123"})
    p2_id = r_patient2.json()["id"]

    client.post("/api/v1/waiting-list/", json={
        "patient_id": created_patient["id"],
        "category": "Neuro Infantil"
    })
    client.post("/api/v1/waiting-list/", json={
        "patient_id": p2_id,
        "category": "Cardio"
    })

    # Filtra por Neuro Infantil
    r_filter = client.get("/api/v1/waiting-list/?category=Neuro+Infantil")
    assert r_filter.status_code == 200
    data = r_filter.json()
    categories = [i["category"] for i in data]
    assert "Neuro Infantil" in categories
    assert "Cardio" not in categories


def test_remove_from_waiting_list_success(client, created_patient):
    r_add = client.post("/api/v1/waiting-list/", json={
        "patient_id": created_patient["id"],
        "category": "Saúde Coletiva"
    })
    item_id = r_add.json()["id"]

    # Remove
    r_del = client.delete(f"/api/v1/waiting-list/{item_id}")
    assert r_del.status_code == 204

    # Tenta obter a lista de espera para verificar se saiu
    r_list = client.get("/api/v1/waiting-list/")
    ids = [i["id"] for i in r_list.json()]
    assert item_id not in ids


def test_remove_from_waiting_list_not_found(client):
    response = client.delete("/api/v1/waiting-list/id_inexistente")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()
