"""Cliente HTTP para comunicação com a API do Orçamentador."""

import requests

from sinapi_client.exceptions import (
    ApiException,
    AuthenticationException,
    NotFoundException,
    RateLimitException,
    ServerException,
)


class HttpClient:
    """Gerencia requisições HTTP para a API."""

    def __init__(self, base_url, api_key, timeout=20):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def get(self, path, params=None):
        """Executa requisição GET.

        Args:
            path: Caminho do endpoint (ex: '/insumos').
            params: Dicionário de parâmetros de query string.

        Returns:
            dict: Dados da resposta JSON.

        Raises:
            ApiException: Em caso de erro na requisição.
        """
        url = self.base_url + path
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ApiException(f"Erro de conexão com a API: {exc}") from exc

        data = None
        try:
            data = response.json()
        except ValueError:
            pass

        if 200 <= response.status_code < 300:
            return data if data is not None else {}

        # Extrai mensagem de erro
        message = "Erro na requisição"
        if isinstance(data, dict):
            message = data.get("erro") or data.get("message") or data.get("mensagem") or message

        if response.status_code in (401, 403):
            raise AuthenticationException(message, response.status_code, data)
        if response.status_code == 404:
            raise NotFoundException(message, response.status_code, data)
        if response.status_code == 429:
            raise RateLimitException(message, response.status_code, data)

        raise ServerException(message, response.status_code, data)
