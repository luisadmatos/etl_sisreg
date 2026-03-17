import os
from pathlib import Path

_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Defina a variável de ambiente DATABASE_URL (ex.: ao usar Docker: "
        "postgresql+psycopg://postgres:password@localhost:5432/sisreg)"
    )

BASE_URL = "https://sisreg-es.saude.gov.br/solicitacao-ambulatorial-{UF}-{MUNICIPIO}"
UF = "MS"
MUNICIPIO = "500830"
