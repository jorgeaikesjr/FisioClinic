"""
test_auth.py — Testes para as rotas de autenticação (Login, Alteração de Senha e Logout).
"""

def test_login_success(unauthenticated_client):
    # O primeiro login deve auto-criar o usuário admin caso ele não exista no banco de testes.
    response = unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert response.json() == {
        "message": "Login realizado com sucesso",
        "must_change_password": False
    }
    # Verifica se o cookie de acesso foi definido
    assert "access_token" in unauthenticated_client.cookies


def test_login_incorrect_credentials(unauthenticated_client):
    # Tentativa com senha errada
    response = unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower() or "incorretos" in response.json()["detail"].lower()


def test_logout(unauthenticated_client):
    # Primeiro realiza o login
    login_resp = unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert login_resp.status_code == 200
    assert "access_token" in unauthenticated_client.cookies

    # Realiza o logout
    logout_resp = unauthenticated_client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json() == {"message": "Logout realizado com sucesso"}
    
    # Verifica se o cookie foi deletado ou invalidado (vazio/removido)
    assert unauthenticated_client.cookies.get("access_token") is None


def test_change_password_flow(unauthenticated_client):
    # 1. Login com a senha antiga
    login_resp = unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert login_resp.status_code == 200

    # 2. Alteração de senha para nova senha
    change_resp = unauthenticated_client.post("/api/v1/auth/change-password", json={
        "old_password": "admin123",
        "new_password": "newadminpassword"
    })
    assert change_resp.status_code == 200
    assert change_resp.json() == {"message": "Senha atualizada com sucesso"}

    # 3. Fazer logout
    unauthenticated_client.post("/api/v1/auth/logout")

    # 4. Tentar logar com a senha antiga (deve falhar)
    fail_resp = unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert fail_resp.status_code == 401

    # 5. Logar com a nova senha (deve funcionar)
    success_resp = unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "newadminpassword"
    })
    assert success_resp.status_code == 200


def test_change_password_wrong_current(unauthenticated_client):
    # Login
    unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    # Tenta mudar passando senha antiga errada
    change_resp = unauthenticated_client.post("/api/v1/auth/change-password", json={
        "old_password": "wrong_current_password",
        "new_password": "some_new_password"
    })
    assert change_resp.status_code == 400
    assert "incorret" in change_resp.json()["detail"].lower()
