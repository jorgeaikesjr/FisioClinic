"""
FisioClinic Launcher
--------------------
Script de entrada para o executável Windows.
Inicia o servidor FastAPI (uvicorn) em background e abre o navegador automaticamente.
"""

import sys
import os
import time
import threading
import webbrowser
import socket

# ─── Resolve os diretórios (funciona tanto para .py quanto para .exe) ──────────
if getattr(sys, 'frozen', False):
    # ── Modo executável PyInstaller ──────────────────────────────────────────
    # BASE_DIR  → diretório onde o .exe está (dados persistentes: db, .env, log)
    # MEIPASS   → diretório temporário com os arquivos empacotados (static, templates)
    BASE_DIR  = os.path.dirname(sys.executable)
    MEIPASS   = sys._MEIPASS
    sys.path.insert(0, MEIPASS)

    # Redireciona stdout/stderr para arquivo de log (evita NoneType.isatty no uvicorn)
    _log = open(os.path.join(BASE_DIR, "app.log"), "a", encoding="utf-8", buffering=1)
    sys.stdout = _log
    sys.stderr = _log

    # Muda para MEIPASS → FastAPI encontra "static/" e "templates/" por caminho relativo
    os.chdir(MEIPASS)

    # ── Banco de dados persistente ───────────────────────────────────────────
    # Na primeira execução, copia o banco inicial do pacote para ao lado do exe.
    db_destino = os.path.join(BASE_DIR, "fisioclinic.db")
    db_bundle  = os.path.join(MEIPASS,  "fisioclinic.db")
    if not os.path.exists(db_destino) and os.path.exists(db_bundle):
        import shutil
        shutil.copy2(db_bundle, db_destino)

    # Define DATABASE_URL com caminho absoluto ANTES de qualquer import da app
    os.environ["DATABASE_URL"] = f"sqlite:///{db_destino}"

    # ── Arquivo .env ─────────────────────────────────────────────────────────
    # Copia .env do pacote para ao lado do exe na primeira execução
    env_destino = os.path.join(BASE_DIR, ".env")
    env_bundle  = os.path.join(MEIPASS,  ".env")
    if not os.path.exists(env_destino) and os.path.exists(env_bundle):
        import shutil
        shutil.copy2(env_bundle, env_destino)

else:
    # ── Modo script Python normal ────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MEIPASS  = None
    os.chdir(BASE_DIR)

# ─── Carrega variáveis do .env (sem sobrescrever as já definidas no ambiente) ──
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    from dotenv import dotenv_values
    for key, value in dotenv_values(env_path).items():
        if key not in os.environ:
            os.environ[key] = value

# ─── Configurações do servidor ─────────────────────────────────────────────────
HOST = "127.0.0.1"
PORT = 8000
URL  = f"http://{HOST}:{PORT}"


def porta_disponivel(host: str, port: int) -> bool:
    """Verifica se a porta está disponível."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) != 0


def aguardar_servidor(host: str, port: int, timeout: int = 30) -> bool:
    """Aguarda o servidor ficar disponível."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def abrir_navegador():
    """Aguarda o servidor e abre o navegador padrão."""
    if aguardar_servidor(HOST, PORT):
        webbrowser.open(URL)
    else:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"O servidor FisioClinic não respondeu em {URL}\n\n"
            f"Verifique se a porta {PORT} está livre e tente novamente.\n\n"
            f"Detalhes em: {os.path.join(BASE_DIR, 'app.log')}",
            "FisioClinic – Erro de Inicialização",
            0x10  # MB_ICONERROR
        )


def main():
    # Verifica se a porta já está em uso
    if not porta_disponivel(HOST, PORT):
        import ctypes
        resp = ctypes.windll.user32.MessageBoxW(
            0,
            f"A porta {PORT} já está em uso.\n\nDeseja abrir o FisioClinic que já está rodando?",
            "FisioClinic",
            0x04 | 0x20  # MB_YESNO | MB_ICONQUESTION
        )
        if resp == 6:  # IDYES
            webbrowser.open(URL)
        return

    # Abre o navegador em thread separada (não bloqueia o servidor)
    threading.Thread(target=abrir_navegador, daemon=True).start()

    # Configura logging mínimo apontando para nosso arquivo de log
    import logging
    logging.basicConfig(
        level=logging.WARNING,
        stream=sys.stderr,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Inicia o servidor uvicorn sem o log_config customizado (evita crash do isatty)
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        log_level="warning",
        access_log=False,
        log_config=None,
    )


if __name__ == "__main__":
    main()
