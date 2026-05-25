"""
test_users.py — Testes para as rotas de gerenciamento de usuários (CRUD e restrição de acesso admin).
"""

def test_create_user_success(client):
    response = client.post("/api/v1/users/", json={
        "username": "novousuario",
        "password": "secretpassword",
        "is_admin": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "novousuario"
    assert data["is_admin"] is False
    assert data["must_change_password"] is True
    assert "id" in data


def test_create_user_duplicate(client):
    payload = {
        "username": "usuario_duplicado",
        "password": "secretpassword",
        "is_admin": False
    }
    # Primeiro sucesso
    r1 = client.post("/api/v1/users/", json=payload)
    assert r1.status_code == 200

    # Segundo deve falhar com 400
    r2 = client.post("/api/v1/users/", json=payload)
    assert r2.status_code == 400
    assert "já existe" in r2.json()["detail"].lower()


def test_list_users(client):
    # Cria dois novos usuários
    client.post("/api/v1/users/", json={"username": "user1", "password": "pwd", "is_admin": False})
    client.post("/api/v1/users/", json={"username": "user2", "password": "pwd", "is_admin": True})

    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2
    
    usernames = [u["username"] for u in users]
    assert "user1" in usernames
    assert "user2" in usernames


def test_delete_user_success(client):
    r_create = client.post("/api/v1/users/", json={
        "username": "usuario_deletar",
        "password": "pwd",
        "is_admin": False
    })
    user_id = r_create.json()["id"]

    # Deleta o usuário
    r_delete = client.delete(f"/api/v1/users/{user_id}")
    assert r_delete.status_code == 204

    # Verifica se ele não está mais listado
    r_list = client.get("/api/v1/users/")
    usernames = [u["username"] for u in r_list.json()]
    assert "usuario_deletar" not in usernames


def test_delete_user_not_found(client):
    response = client.delete("/api/v1/users/id_inexistente")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()


def test_delete_self_returns_400(client):
    # O mock_user no fixture padrão client possui id="test-admin-id".
    # Primeiro, criamos esse usuário no banco de testes (para que ele exista no banco).
    from core.database import SessionLocal
    from models.user import User
    from core.security import get_password_hash

    db = SessionLocal()
    try:
        db_user = User(
            id="test-admin-id",
            username="admin_self",
            hashed_password=get_password_hash("pwd"),
            is_admin=True,
            must_change_password=False
        )
        db.merge(db_user)
        db.commit()
    finally:
        db.close()

    # Tenta excluir a si mesmo
    response = client.delete("/api/v1/users/test-admin-id")
    assert response.status_code == 400
    assert "não pode excluir a si mesmo" in response.json()["detail"].lower()


def test_require_admin_protection(unauthenticated_client):
    # Acesso não autenticado a rotas protegidas por admin deve retornar 401 Unauthorized
    r_get = unauthenticated_client.get("/api/v1/users/")
    assert r_get.status_code == 401

    r_post = unauthenticated_client.post("/api/v1/users/", json={
        "username": "hack_attempt",
        "password": "pwd"
    })
    assert r_post.status_code == 401

    r_del = unauthenticated_client.delete("/api/v1/users/some-id")
    assert r_del.status_code == 401


def test_authenticated_non_admin_cannot_access_user_endpoints(client):
    from main import app
    from core.auth import require_auth, require_admin, get_current_user
    from models.user import User
    from fastapi import HTTPException

    non_admin_user = User(
        id="test-non-admin-id",
        username="nonadmin",
        is_admin=False,
        must_change_password=False
    )

    app.dependency_overrides[require_auth] = lambda: non_admin_user
    app.dependency_overrides[get_current_user] = lambda: non_admin_user
    
    def mock_require_admin():
        raise HTTPException(status_code=403, detail="Acesso negado. Requer privilégios de administrador.")
    
    app.dependency_overrides[require_admin] = mock_require_admin

    try:
        r_get = client.get("/api/v1/users/")
        assert r_get.status_code == 403

        r_post = client.post("/api/v1/users/", json={
            "username": "new_user_attempt",
            "password": "somepassword",
            "is_admin": False
        })
        assert r_post.status_code == 403

        r_del = client.delete("/api/v1/users/some-id")
        assert r_del.status_code == 403
    finally:
        app.dependency_overrides.clear()

