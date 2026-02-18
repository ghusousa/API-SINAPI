"""
Cliente Python para a API SINAPI do Orçamentador.

Uso básico:
    from sinapi_client import Client

    client = Client(api_key="SUA_API_KEY")
    insumos = client.insumos.buscar(nome="cimento", estado="sp", limit=10)
"""

from sinapi_client.client import Client
from sinapi_client.exceptions import (
    ApiException,
    AuthenticationException,
    NotFoundException,
    RateLimitException,
    ServerException,
)

__all__ = [
    "Client",
    "ApiException",
    "AuthenticationException",
    "NotFoundException",
    "RateLimitException",
    "ServerException",
]
