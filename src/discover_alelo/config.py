"""Configuração centralizada do projeto.

Carrega variáveis de ambiente do `.env` e valida as obrigatórias.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Resolve a raiz do projeto baseando-se na localização deste arquivo
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _find_env_file() -> Path:
    """Localiza o .env na raiz do projeto."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        # Tenta um nível acima (caso executado de dentro de src/)
        alt = PROJECT_ROOT.parent / ".env"
        if alt.exists():
            return alt
    return env_path


# Carrega .env automaticamente no import
_env_path = _find_env_file()
load_dotenv(_env_path)


# ─── Variáveis obrigatórias ─────────────────────────────────────────────────

REQUIRED_VARS = [
    "ALELO_AUTH_URL",
    "ALELO_API_BASE_URL",
    "ALELO_CLIENT_ID",
    "ALELO_CLIENT_SECRET",
    "ALELO_BASIC_AUTH",
    "ALELO_FNP",
    "ALELO_USER_ID",
    "ALELO_IBM_CLIENT_ID",
]


def validate_env() -> dict[str, str]:
    """Valida que todas as variáveis obrigatórias estão definidas.

    Returns:
        Dicionário com todas as variáveis carregadas.

    Raises:
        SystemExit: Se alguma variável obrigatória estiver ausente.
    """
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        print("❌ Variáveis de ambiente obrigatórias ausentes:", file=sys.stderr)
        for var in missing:
            print(f"   - {var}", file=sys.stderr)
        print(
            f"\n   Crie o arquivo .env na raiz do projeto: {PROJECT_ROOT / '.env'}",
            file=sys.stderr,
        )
        sys.exit(1)

    return get_all_config()


def get_all_config() -> dict[str, str]:
    """Retorna todas as configurações carregadas do ambiente."""
    return {
        # Autenticação
        "auth_url": os.getenv("ALELO_AUTH_URL", ""),
        "api_base_url": os.getenv("ALELO_API_BASE_URL", ""),
        "client_id": os.getenv("ALELO_CLIENT_ID", ""),
        "client_secret": os.getenv("ALELO_CLIENT_SECRET", ""),
        "basic_auth": os.getenv("ALELO_BASIC_AUTH", ""),
        "fnp": os.getenv("ALELO_FNP", ""),
        "user_id": os.getenv("ALELO_USER_ID", ""),
        "ibm_client_id": os.getenv("ALELO_IBM_CLIENT_ID", ""),
        # Aplicação
        "auth_type": os.getenv("ALELO_AUTH_TYPE", "IS-ALELO"),
        "app_version": os.getenv("ALELO_APP_VERSION", ""),
        "platform": os.getenv("ALELO_PLATFORM", "IOS"),
        # Runtime
        "timeout": int(os.getenv("ALELO_REQUEST_TIMEOUT", "60")),
        "verify_ssl": os.getenv("ALELO_VERIFY_SSL", "true").lower() == "true",
    }


def is_homologacao_url(url: str) -> bool:
    """Verifica se a URL pertence ao ambiente de homologação.

    Retorna True se a URL contém indicadores de homologação/UAT/sandbox/hml.
    """
    indicators = ["homologacao", "uat", "sandbox", "hml"]
    url_lower = url.lower()
    return any(indicator in url_lower for indicator in indicators)


def get_project_root() -> Path:
    """Retorna o caminho absoluto da raiz do projeto."""
    return PROJECT_ROOT
