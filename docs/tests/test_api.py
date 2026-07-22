import re
from pathlib import Path

import requests


ARQUIVO_CURL = Path("request_sample.txt")


def carregar_curl(arquivo: Path) -> tuple[str, dict[str, str]]:
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo.resolve()}"
        )

    conteudo = arquivo.read_text(encoding="utf-8")

    # Extrai a URL completa, inclusive ?lang=pt
    resultado_url = re.search(
        r'https?://[^\s"\'\\]+',
        conteudo,
    )

    if not resultado_url:
        raise ValueError("Não foi possível encontrar a URL no TXT.")

    url = resultado_url.group(0)

    # Extrai todos os headers declarados com -H
    headers_encontrados = re.findall(
        r'-H\s+["\']([^:]+):\s*(.*?)["\']',
        conteudo,
        flags=re.DOTALL,
    )

    headers = {
        nome.strip(): valor.strip()
        for nome, valor in headers_encontrados
    }

    return url, headers


def main() -> None:
    url, headers = carregar_curl(ARQUIVO_CURL)

    print("URL:", url)
    print("Headers encontrados:", list(headers.keys()))

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        print("Status:", response.status_code)

        try:
            print("Resposta JSON:")
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Resposta:")
            print(response.text)

        response.raise_for_status()

    except requests.exceptions.HTTPError as erro:
        print("Erro HTTP:", erro)
        print("Resposta da API:", response.text)

    except requests.exceptions.Timeout:
        print("A API demorou mais de 30 segundos para responder.")

    except requests.exceptions.ConnectionError as erro:
        print("Erro de conexão:", erro)

    except requests.exceptions.RequestException as erro:
        print("Erro na requisição:", erro)


if __name__ == "__main__":
    main()