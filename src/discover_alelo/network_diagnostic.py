"""Diagnóstico de rede antes da autenticação.

Verifica se o endpoint é alcançável sem expor dados sensíveis.
"""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests


@dataclass
class NetworkDiagnostic:
    """Resultado do diagnóstico de rede."""

    host: str = ""
    port: int = 443
    dns_resolved: bool = False
    dns_ip: str = ""
    dns_duration_ms: int = 0
    tcp_reachable: bool = False
    tcp_duration_ms: int = 0
    https_status: int = 0
    https_duration_ms: int = 0
    content_type: str = ""
    correlation_id: str = ""
    proxy_detected: bool = False
    overall_status: str = ""
    error_detail: str = ""
    hypothesis: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "dns_resolved": self.dns_resolved,
            "dns_ip": self.dns_ip,
            "dns_duration_ms": self.dns_duration_ms,
            "tcp_reachable": self.tcp_reachable,
            "tcp_duration_ms": self.tcp_duration_ms,
            "https_status": self.https_status,
            "https_duration_ms": self.https_duration_ms,
            "content_type": self.content_type,
            "correlation_id": self.correlation_id,
            "proxy_detected": self.proxy_detected,
            "overall_status": self.overall_status,
            "error_detail": self.error_detail,
            "hypothesis": self.hypothesis,
        }


def diagnose_endpoint(url: str, connect_timeout: int = 10) -> NetworkDiagnostic:
    """Executa diagnóstico de rede para um endpoint.

    Não envia credenciais. Apenas verifica alcançabilidade.

    Args:
        url: URL do endpoint a verificar.
        connect_timeout: Timeout para conexão TCP.

    Returns:
        NetworkDiagnostic com os resultados.
    """
    diag = NetworkDiagnostic()
    parsed = urlparse(url)
    diag.host = parsed.hostname or ""
    diag.port = parsed.port or 443

    if not diag.host:
        diag.overall_status = "DNS_ERROR"
        diag.error_detail = "Host não extraído da URL"
        return diag

    # 1. Resolução DNS
    start = time.time()
    try:
        ip = socket.gethostbyname(diag.host)
        diag.dns_resolved = True
        diag.dns_ip = ip
    except socket.gaierror as e:
        diag.dns_resolved = False
        diag.overall_status = "DNS_ERROR"
        diag.error_detail = f"Resolução DNS falhou: {type(e).__name__}"
        diag.hypothesis = (
            "O host não foi resolvido. Possíveis causas: "
            "VPN desconectada, DNS corporativo inacessível, host incorreto."
        )
        return diag
    finally:
        diag.dns_duration_ms = int((time.time() - start) * 1000)

    # 2. Conexão TCP
    start = time.time()
    try:
        sock = socket.create_connection(
            (diag.host, diag.port), timeout=connect_timeout
        )
        sock.close()
        diag.tcp_reachable = True
    except (socket.timeout, OSError) as e:
        diag.tcp_reachable = False
        diag.overall_status = "CONNECTION_ERROR"
        diag.error_detail = f"Conexão TCP falhou: {type(e).__name__}"
        diag.hypothesis = (
            "O host foi resolvido mas a porta não está acessível. "
            "Possíveis causas: firewall, VPN necessária, proxy bloqueando."
        )
        return diag
    finally:
        diag.tcp_duration_ms = int((time.time() - start) * 1000)

    # 3. Request HTTPS sem credenciais (apenas verifica se o gateway responde)
    start = time.time()
    try:
        # Faz um HEAD ou OPTIONS na raiz — não no endpoint exato
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        resp = requests.head(
            base_url,
            timeout=(connect_timeout, 15),
            verify=True,
            allow_redirects=False,
        )
        diag.https_status = resp.status_code
        diag.content_type = resp.headers.get("content-type", "")
        diag.correlation_id = resp.headers.get(
            "x-correlation-id",
            resp.headers.get("x-request-id", ""),
        )

        # Detecta proxy
        via = resp.headers.get("via", "")
        if via:
            diag.proxy_detected = True

    except requests.exceptions.SSLError as e:
        diag.overall_status = "CONNECTION_ERROR"
        diag.error_detail = f"Erro SSL: {type(e).__name__}"
        diag.hypothesis = "Certificado SSL inválido ou intermediário. Verificar proxy corporativo."
        return diag
    except requests.exceptions.Timeout:
        diag.overall_status = "GATEWAY_TIMEOUT"
        diag.error_detail = "Timeout aguardando resposta HTTPS do gateway"
        diag.hypothesis = (
            "O host é alcançável por TCP mas não respondeu HTTP. "
            "Possível gateway timeout ou firewall descartando pacotes."
        )
        return diag
    except requests.exceptions.ConnectionError as e:
        diag.overall_status = "CONNECTION_ERROR"
        diag.error_detail = f"Erro de conexão HTTPS: {type(e).__name__}"
        return diag
    finally:
        diag.https_duration_ms = int((time.time() - start) * 1000)

    # 4. Classificação final
    if diag.https_status in (200, 301, 302, 403, 404, 405):
        diag.overall_status = "AUTH_ENDPOINT_RESPONDED"
    elif diag.https_status == 503:
        diag.overall_status = "SERVICE_UNAVAILABLE"
        diag.hypothesis = "Gateway retornou 503. O serviço pode estar em manutenção."
    elif diag.https_status == 502:
        diag.overall_status = "SERVICE_UNAVAILABLE"
        diag.hypothesis = "Bad gateway (502). Backend do auth pode estar fora."
    elif diag.https_status == 0:
        diag.overall_status = "CONNECTION_ERROR"
    else:
        diag.overall_status = "NETWORK_REACHABLE"

    return diag
