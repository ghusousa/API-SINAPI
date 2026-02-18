"""Módulo de proxy para a API do Orçamentador.

Encaminha as requisições recebidas pela nossa API para a API oficial
do Orçamentador, repassando os mesmos parâmetros e headers de autenticação.
"""

import os

import httpx

from fastapi import HTTPException

UPSTREAM_BASE_URL = os.environ.get(
    "UPSTREAM_BASE_URL", "https://orcamentador.com.br/api"
)
UPSTREAM_API_KEY = os.environ.get("UPSTREAM_API_KEY", "")
UPSTREAM_TIMEOUT = int(os.environ.get("UPSTREAM_TIMEOUT", "20"))


async def proxy_request(path: str, query_params) -> dict:
    """Faz proxy de uma requisição para a API upstream do Orçamentador.

    Args:
        path: Caminho do endpoint (ex: ``/insumos``).
        query_params: Parâmetros de query string recebidos na requisição.

    Returns:
        dict: Resposta JSON da API upstream.

    Raises:
        HTTPException: Quando a API upstream retorna erro.
    """
    if not UPSTREAM_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="UPSTREAM_API_KEY não configurada no servidor",
        )

    url = UPSTREAM_BASE_URL.rstrip("/") + path
    headers = {
        "X-API-Key": UPSTREAM_API_KEY,
        "Accept": "application/json",
    }

    params = dict(query_params)

    async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="Erro de conexão com a API upstream",
            )

    if 200 <= response.status_code < 300:
        try:
            return response.json()
        except ValueError:
            return {}

    # Repassa o erro da API upstream
    try:
        data = response.json()
    except ValueError:
        data = {"erro": response.text}

    message = "Erro na API upstream"
    if isinstance(data, dict):
        message = (
            data.get("erro")
            or data.get("message")
            or data.get("mensagem")
            or message
        )

    raise HTTPException(status_code=response.status_code, detail=message)
