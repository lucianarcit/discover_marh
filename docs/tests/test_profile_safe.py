"""
Teste seguro do endpoint GET /profile da API Alelo HRM.

Objetivo:
    Validar conectividade e autenticação com a API HRM usando um access token
    obtido manualmente do app Meu Alelo HML.

Segurança:
    - Token obtido via getpass (interativo) ou variável de ambiente ALELO_ACCESS_TOKEN.
    - Nenhuma credencial é impressa, logada ou persistida.
    - Resposta sanitizada: CPF, e-mail, telefone e nome são mascarados.
    - TLS habilitado (verify=True); timeout explícito.
    - Somente GET; nenhuma operação de escrita.

Configuração:
    O script carrega variáveis do arquivo docs/tests/.env.example (ou .env)
    localizado no mesmo diretório. Preencha os valores nesse arquivo OU defina
    variáveis de ambiente na sessão. Variáveis de ambiente têm prioridade.

    IMPORTANTE: Nunca faça commit do .env.example com valores reais.
    Adicione ao .gitignore se necessário.

Variáveis obrigatórias:
    ALELO_CLIENT_ID        - Client ID Sensedia
    ALELO_CLIENT_SECRET    - Client Secret Sensedia
    ALELO_USER_ID          - ID do usuário HML
    ALELO_FNP              - Device fingerprint

Variáveis opcionais:
    ALELO_ACCESS_TOKEN     - Se definido, evita prompt interativo
    ALELO_APP_VERSION      - Default: 8.55.0 (2026071702)
    ALELO_PLATFORM         - Default: IOS
    ALELO_API_BASE_URL     - Default: URL HML
    ALELO_API_TIMEOUT_SECONDS - Default: 15

Uso:
    # Opção 1 — Preencher .env.example e executar (token pedido via getpass):
    python docs/tests/test_profile_safe.py

    # Opção 2 — Tudo via variáveis de ambiente:
    set ALELO_CLIENT_ID=<valor>
    set ALELO_CLIENT_SECRET=<valor>
    set ALELO_USER_ID=<valor>
    set ALELO_FNP=<valor>
    set ALELO_ACCESS_TOKEN=<valor>
    python docs/tests/test_profile_safe.py

Como obter o access token:
    1. Abra o app Meu Alelo apontado para HML.
    2. Faça login (CPF + senha de HML).
    3. Intercepte o accessToken via proxy (Charles/Proxyman).
    4. Cole no .env.example ou digite no prompt interativo.
    5. O token expira em ~300 segundos — re-obtenha se receber 401.
"""

import base64
import getpass
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Erro: biblioteca 'requests' não instalada.")
    print("Instale com: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Erro: biblioteca 'python-dotenv' não instalada.")
    print("Instale com: pip install python-dotenv")
    sys.exit(1)


# ─── Carregar .env do diretório do script ────────────────────────────────────

_script_dir = Path(__file__).resolve().parent
_env_file = _script_dir / ".env.example"

if _env_file.exists():
    load_dotenv(_env_file, override=False)
else:
    # Tentar .env no mesmo diretório
    _env_alt = _script_dir / ".env"
    if _env_alt.exists():
        load_dotenv(_env_alt, override=False)


# ─── Configuração via variáveis de ambiente ──────────────────────────────────

def get_required_env(name: str) -> str:
    """Lê variável de ambiente obrigatória. Aborta se ausente."""
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Erro: variável de ambiente '{name}' não definida.")
        print(f"Defina antes de executar: set {name}=<valor>")
        sys.exit(1)
    return value


def get_optional_env(name: str, default: str) -> str:
    """Lê variável de ambiente opcional com valor default."""
    return os.environ.get(name, "").strip() or default


# ─── Obtenção segura do token ────────────────────────────────────────────────

def get_access_token() -> str:
    """
    Obtém o access token de forma segura.
    Prioridade:
        1. Variável de ambiente ALELO_ACCESS_TOKEN
        2. Entrada interativa via getpass (não exibe o valor)
    """
    token = os.environ.get("ALELO_ACCESS_TOKEN", "").strip()
    if token:
        return token

    print()
    print("Access token não encontrado em ALELO_ACCESS_TOKEN.")
    print("Digite o token obtido do app Meu Alelo HML (não será exibido):")
    token = getpass.getpass(prompt="  Token: ")
    if not token.strip():
        print("Erro: token vazio. Abortando.")
        sys.exit(1)
    return token.strip()


# ─── Sanitização de dados pessoais ───────────────────────────────────────────

def mask_cpf(cpf: str) -> str:
    """Mascara CPF: ***.XXX.***-** (exibe apenas 3 dígitos centrais)."""
    if not cpf or len(cpf) < 11:
        return "***"
    clean = cpf.replace(".", "").replace("-", "").replace(" ", "")
    if len(clean) >= 11:
        return f"***.{clean[3:6]}.***-**"
    return "***"


def mask_email(email: str) -> str:
    """Mascara e-mail: primeiro caractere + ***@domínio parcial."""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain[0]}***"


def mask_phone(phone_obj) -> str:
    """Mascara telefone."""
    if not phone_obj:
        return "***"
    return "(**) *****-****"


# ─── Tratamento de erros HTTP ────────────────────────────────────────────────

def handle_http_error(response: requests.Response) -> None:
    """Trata erros HTTP com mensagens descritivas e seguras."""
    status = response.status_code

    print(f"\n─── Resultado ───")
    print(f"HTTP {status}")

    if status == 401:
        print()
        print("⚠️  O access token pode ter expirado (TTL ~300s).")
        print("   Obtenha um novo token no app Meu Alelo HML e re-execute.")
    elif status == 403:
        print()
        print("⚠️  Acesso negado (403 Forbidden).")
        print("   O token é válido mas não tem autorização para este recurso.")
        print("   Não será feita tentativa de renovação.")
    elif status == 429:
        print()
        print("⚠️  Limite de requisições atingido (429 Too Many Requests).")
        print("   Aguarde alguns minutos antes de tentar novamente.")
    elif 500 <= status < 600:
        print()
        print(f"⚠️  Erro do servidor ({status}).")
        print("   A API está temporariamente indisponível. Tente novamente mais tarde.")
    elif status == 400:
        print()
        print("⚠️  Requisição inválida (400 Bad Request).")
        print("   Verifique se os headers estão corretos.")
    else:
        print()
        print(f"⚠️  Erro inesperado: HTTP {status}")

    # Nunca exibir corpo de erro que pode conter dados sensíveis
    sys.exit(1)


# ─── Execução principal ──────────────────────────────────────────────────────

def main():
    # Ler configurações
    client_id = get_required_env("ALELO_CLIENT_ID")
    client_secret = get_required_env("ALELO_CLIENT_SECRET")
    user_id = get_required_env("ALELO_USER_ID")
    fnp = get_required_env("ALELO_FNP")
    app_version = get_optional_env("ALELO_APP_VERSION", "8.55.0 (2026071702)")
    platform = get_optional_env("ALELO_PLATFORM", "IOS")
    base_url = get_optional_env(
        "ALELO_API_BASE_URL",
        "https://api-ma.homologacaoalelo.com.br/alelo/uat/cardholders-hr-management/v1",
    )
    timeout = int(get_optional_env("ALELO_API_TIMEOUT_SECONDS", "15"))

    # Obter token de forma segura
    access_token = get_access_token()

    # Calcular X-BASIC-AUTHORIZATION
    basic_auth = "Basic " + base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    # Montar headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "CLIENT_ID": client_id,
        "CLIENT_SECRET": client_secret,
        "X-BASIC-AUTHORIZATION": basic_auth,
        "x-ibm-client-id": client_id,
        "APP_VERSION": app_version,
        "PLATFORM": platform,
        "FNP": fnp,
        "user_id": user_id,
        "AUTH_TYPE": "IS-ALELO",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Exibir configuração sanitizada
    print()
    print("─── Configuração ───")
    print(f"API Base URL: {base_url}")
    print(f"Endpoint:    GET /profile")
    print(f"Timeout:     {timeout}s")
    print(f"TLS:         habilitado (verify=True)")
    print(f"Token:       recebido de forma segura (não será exibido)")
    print(f"Plataforma:  {platform}")
    print(f"App Version: {app_version}")
    print()

    # Executar requisição
    url = f"{base_url}/profile"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=True,
        )
    except requests.exceptions.ConnectionError as e:
        print("─── Resultado ───")
        print("❌ Erro de conexão.")
        print("   Verifique se a URL está acessível e se há conectividade de rede.")
        print(f"   Detalhe técnico: {type(e).__name__}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("─── Resultado ───")
        print(f"❌ Timeout após {timeout}s.")
        print("   A API não respondeu dentro do tempo limite.")
        sys.exit(1)
    except requests.exceptions.SSLError as e:
        print("─── Resultado ───")
        print("❌ Erro TLS/SSL.")
        print("   Falha na validação do certificado.")
        print(f"   Detalhe técnico: {type(e).__name__}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print("─── Resultado ───")
        print(f"❌ Erro na requisição: {type(e).__name__}")
        sys.exit(1)

    # Verificar status
    if response.status_code != 200:
        handle_http_error(response)
        return

    # Parsear resposta
    try:
        body = response.json()
    except ValueError:
        print("─── Resultado ───")
        print("HTTP 200 — mas resposta não é JSON válido.")
        print("Conteúdo não será exibido por segurança.")
        sys.exit(1)

    # Validar estrutura esperada
    if not isinstance(body, dict):
        print("─── Resultado ───")
        print("HTTP 200 — mas estrutura da resposta inesperada (não é objeto).")
        sys.exit(1)

    # Exibir resultado sanitizado
    print("─── Resultado ───")
    print("HTTP 200 OK")
    print()

    # functionType — dado principal do teste
    functions = body.get("functions", [])
    if functions:
        for func in functions:
            ft = func.get("functionType", "desconhecido")
            print(f"  functionType: {ft}")
    else:
        print("  functionType: (não encontrado na resposta)")

    # Campos sanitizados
    cpf = body.get("documentNumber", "")
    email = body.get("email", "")
    name = body.get("name", "")
    phone = body.get("primaryPhone")

    print()
    print(f"  documentNumber: {mask_cpf(cpf)}")
    print(f"  name: *** (omitido)")
    print(f"  email: {mask_email(email)}")
    print(f"  phone: {mask_phone(phone)}")
    print(f"  idResponsible: ***")

    # Campos extras que podem estar presentes
    if "brithDate" in body:
        print(f"  brithDate: *** (omitido)")
    if "nameDepartment" in body:
        print(f"  nameDepartment: *** (omitido)")

    print()
    print("✅ Teste concluído com sucesso.")
    print("   Campos sensíveis mascarados conforme política de segurança.")


if __name__ == "__main__":
    main()
