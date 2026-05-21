# -*- mode: python ; coding: utf-8 -*-
#
# FisioClinic – PyInstaller spec
# Execute com: pyinstaller fisioclinic.spec
#

import os

block_cipher = None

# ─── Dados extras a serem incluídos no executável ─────────────────────────────
# Formato: (origem, destino_dentro_do_bundle)
datas = [
    # Pastas de templates e arquivos estáticos
    ("templates",   "templates"),
    ("static",      "static"),
    # Banco de dados inicial (será copiado apenas se não existir no diretório do exe)
    ("fisioclinic.db", "."),
    # Arquivo de configuração
    (".env",        "."),
]

# ─── Módulos ocultos que o PyInstaller não detecta automaticamente ─────────────
hiddenimports = [
    # FastAPI / Starlette internals
    "fastapi",
    "fastapi.middleware",
    "fastapi.staticfiles",
    "fastapi.templating",
    "starlette",
    "starlette.middleware",
    "starlette.middleware.sessions",
    "starlette.routing",
    "starlette.staticfiles",
    "starlette.templating",
    # Uvicorn
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    # SQLAlchemy
    "sqlalchemy",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.orm",
    # Pydantic
    "pydantic",
    "pydantic_settings",
    # Jinja2
    "jinja2",
    "jinja2.ext",
    # python-dotenv (usado no launcher)
    "dotenv",
    # Bcrypt / PyJWT
    "bcrypt",
    "jwt",
    # Outros
    "multipart",
    "email",
    "email.mime",
    "email.mime.text",
    # Módulos da aplicação
    "main",
    "core.config",
    "core.database",
    "core.auth",
    "core.security",
    "models.base",
    "models.patient",
    "models.intern",
    "models.appointment",
    "models.waiting_list",
    "models.fitting_list",
    "models.user",
    "api.routers.patients",
    "api.routers.interns",
    "api.routers.appointments",
    "api.routers.views",
    "api.routers.reports",
    "api.routers.settings",
    "api.routers.waiting_list",
    "api.routers.fitting_list",
    "api.routers.auth",
    "api.routers.users",
    "schemas",
    "services",
]

a = Analysis(
    ["launcher.py"],          # Script de entrada
    pathex=["."],             # Raiz do projeto
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Remove dependências desnecessárias para reduzir tamanho
        "psycopg2",
        "psycopg2-binary",
        "pytest",
        "httpx",
        "pytest_cov",
        "pandas",
        "xlrd",
        "openpyxl",
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "IPython",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="FisioClinic",            # Nome do executável gerado
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                      # Compressão UPX (reduz tamanho ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                 # SEM janela de terminal (windowed mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets\\fisioclinic.ico",  # Ícone personalizado
    version=None,
)
