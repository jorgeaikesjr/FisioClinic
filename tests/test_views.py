"""
test_views.py — Testes para as rotas HTML do frontend (views).
"""

# Rotas públicas ou que não exigem autenticação ativa (ou têm comportamento específico)
def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "login" in response.text.lower()


def test_change_password_page_renders(client):
    response = client.get("/change-password")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "senha" in response.text.lower()


# Rotas protegidas acessadas por usuário autenticado
def test_protected_pages_render_when_authenticated(client):
    paths = [
        "/",
        "/calendar",
        "/patients",
        "/interns",
        "/fitting-list",
        "/waiting-list",
        "/system-users",
        "/reports/absences",
        "/reports/weekly-summary",
        "/reports/waiting-list",
        "/reports/attendance",
        "/reports/patient-attendance"
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, f"Erro ao renderizar rota {path}"
        assert "text/html" in response.headers["content-type"]


# Rotas protegidas acessadas sem autenticação (devem redirecionar para /login)
def test_protected_pages_redirect_when_unauthenticated(unauthenticated_client):
    paths = [
        "/",
        "/calendar",
        "/patients",
        "/interns",
        "/fitting-list",
        "/waiting-list",
        "/system-users",
        "/reports/absences",
        "/reports/weekly-summary",
        "/reports/waiting-list",
        "/reports/attendance",
        "/reports/patient-attendance"
    ]
    for path in paths:
        response = unauthenticated_client.get(path, follow_redirects=False)
        assert response.status_code == 307, f"Rota {path} não redirecionou"
        assert response.headers["location"] == "/login"


# Teste para MustChangePasswordException redirecionando para /change-password
def test_must_change_password_redirects_to_change_password(unauthenticated_client):
    from core.database import SessionLocal
    from models.user import User
    from core.security import get_password_hash

    # Cria um usuário que DEVE alterar a senha no primeiro login
    db = SessionLocal()
    try:
        user = User(
            username="temp_user",
            hashed_password=get_password_hash("temp123"),
            is_admin=False,
            must_change_password=True
        )
        db.merge(user)
        db.commit()
    finally:
        db.close()

    # Faz login com o usuário temporário
    login_resp = unauthenticated_client.post("/api/v1/auth/login", json={
        "username": "temp_user",
        "password": "temp123"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["must_change_password"] is True

    # Tenta acessar a página inicial (deve redirecionar para /change-password)
    response = unauthenticated_client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/change-password"


def test_system_users_page_requires_admin(client):
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
        raise HTTPException(status_code=403, detail="Acesso negado")
    app.dependency_overrides[require_admin] = mock_require_admin

    try:
        response = client.get("/system-users")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()

