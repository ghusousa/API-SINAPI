"""Testes unitários para o cliente da API SINAPI."""

import os
from unittest.mock import patch, MagicMock

import pytest

from sinapi_client import Client
from sinapi_client.client import BASE_URL
from sinapi_client.exceptions import (
    ApiException,
    AuthenticationException,
    NotFoundException,
    RateLimitException,
    ServerException,
)


# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

class TestClientInit:
    def test_client_with_api_key(self):
        client = Client(api_key="test-key")
        assert client._http.api_key == "test-key"
        assert client._http.base_url == BASE_URL

    def test_client_with_env_var(self):
        with patch.dict(os.environ, {"ORCAMENTADOR_API_KEY": "env-key"}):
            client = Client()
            assert client._http.api_key == "env-key"

    def test_client_missing_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ORCAMENTADOR_API_KEY", None)
            with pytest.raises(ValueError):
                Client()

    def test_client_custom_base_url(self):
        client = Client(api_key="k", base_url="https://custom.api")
        assert client._http.base_url == "https://custom.api"

    def test_client_resources_exist(self):
        client = Client(api_key="k")
        assert client.insumos is not None
        assert client.composicoes is not None
        assert client.encargos is not None
        assert client.indicadores is not None
        assert client.estados is not None
        assert client.orcamento is not None


# ---------------------------------------------------------------------------
# HttpClient
# ---------------------------------------------------------------------------

class TestHttpClient:
    def _mock_response(self, status_code=200, json_data=None, raise_exc=False):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data if json_data is not None else {}
        if raise_exc:
            import requests
            resp.json.side_effect = ValueError
        return resp

    @patch("sinapi_client.http_client.requests.get")
    def test_successful_get(self, mock_get):
        mock_get.return_value = self._mock_response(200, {"data": [1, 2]})
        client = Client(api_key="k")
        result = client._http.get("/test", params={"a": "1"})
        assert result == {"data": [1, 2]}
        mock_get.assert_called_once()

    @patch("sinapi_client.http_client.requests.get")
    def test_auth_error(self, mock_get):
        mock_get.return_value = self._mock_response(401, {"erro": "Não autorizado"})
        client = Client(api_key="k")
        with pytest.raises(AuthenticationException) as exc_info:
            client._http.get("/test")
        assert "Não autorizado" in str(exc_info.value)

    @patch("sinapi_client.http_client.requests.get")
    def test_forbidden_error(self, mock_get):
        mock_get.return_value = self._mock_response(403, {"message": "Proibido"})
        client = Client(api_key="k")
        with pytest.raises(AuthenticationException):
            client._http.get("/test")

    @patch("sinapi_client.http_client.requests.get")
    def test_not_found_error(self, mock_get):
        mock_get.return_value = self._mock_response(404, {"mensagem": "Não encontrado"})
        client = Client(api_key="k")
        with pytest.raises(NotFoundException):
            client._http.get("/test")

    @patch("sinapi_client.http_client.requests.get")
    def test_rate_limit_error(self, mock_get):
        mock_get.return_value = self._mock_response(429, {"erro": "Rate limit"})
        client = Client(api_key="k")
        with pytest.raises(RateLimitException):
            client._http.get("/test")

    @patch("sinapi_client.http_client.requests.get")
    def test_server_error(self, mock_get):
        mock_get.return_value = self._mock_response(500, {"erro": "Interno"})
        client = Client(api_key="k")
        with pytest.raises(ServerException):
            client._http.get("/test")

    @patch("sinapi_client.http_client.requests.get")
    def test_connection_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.ConnectionError("fail")
        client = Client(api_key="k")
        with pytest.raises(ApiException):
            client._http.get("/test")

    @patch("sinapi_client.http_client.requests.get")
    def test_headers_sent(self, mock_get):
        mock_get.return_value = self._mock_response(200, {})
        client = Client(api_key="my-key")
        client._http.get("/x")
        _, kwargs = mock_get.call_args
        assert kwargs["headers"]["X-API-Key"] == "my-key"
        assert kwargs["headers"]["Accept"] == "application/json"


# ---------------------------------------------------------------------------
# Insumos
# ---------------------------------------------------------------------------

class TestInsumos:
    @patch("sinapi_client.http_client.requests.get")
    def test_buscar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"insumos": []})
        client = Client(api_key="k")
        result = client.insumos.buscar(nome="cimento", estado="sp")
        assert result == {"insumos": []}

    @patch("sinapi_client.http_client.requests.get")
    def test_historico(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"historico": []})
        client = Client(api_key="k")
        result = client.insumos.historico(codigo=123, estado="sp")
        assert result == {"historico": []}
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["item"] == "insumo"

    @patch("sinapi_client.http_client.requests.get")
    def test_comparar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
        client = Client(api_key="k")
        client.insumos.comparar(codigo=123, estados="sp,rj")
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["item"] == "insumo"

    @patch("sinapi_client.http_client.requests.get")
    def test_previsao(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
        client = Client(api_key="k")
        client.insumos.previsao(codigo=123, estado="sp", regime="DESONERADO")
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["item"] == "insumo"
        assert kwargs["params"]["regime"] == "DESONERADO"


# ---------------------------------------------------------------------------
# Composições
# ---------------------------------------------------------------------------

class TestComposicoes:
    @patch("sinapi_client.http_client.requests.get")
    def test_buscar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"composicoes": []})
        client = Client(api_key="k")
        result = client.composicoes.buscar(nome="argamassa", estado="sp")
        assert result == {"composicoes": []}

    @patch("sinapi_client.http_client.requests.get")
    def test_detalhar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"detalhes": {}})
        client = Client(api_key="k")
        result = client.composicoes.detalhar(codigo=123456, estado="sp")
        assert result == {"detalhes": {}}

    @patch("sinapi_client.http_client.requests.get")
    def test_explode(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"insumos": []})
        client = Client(api_key="k")
        result = client.composicoes.explode(codigo=123456, estado="sp")
        assert result == {"insumos": []}

    @patch("sinapi_client.http_client.requests.get")
    def test_historico(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
        client = Client(api_key="k")
        client.composicoes.historico(codigo=123456, estado="sp")
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["item"] == "composicao"

    @patch("sinapi_client.http_client.requests.get")
    def test_comparar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
        client = Client(api_key="k")
        client.composicoes.comparar(codigo=123456, estados="sp,rj,pb")
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["item"] == "composicao"

    @patch("sinapi_client.http_client.requests.get")
    def test_previsao(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
        client = Client(api_key="k")
        client.composicoes.previsao(codigo=123456, estado="sp", regime="NAO_DESONERADO")
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["item"] == "composicao"


# ---------------------------------------------------------------------------
# Encargos, Indicadores, Estados, Orçamento
# ---------------------------------------------------------------------------

class TestEncargos:
    @patch("sinapi_client.http_client.requests.get")
    def test_buscar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"encargos": []})
        client = Client(api_key="k")
        result = client.encargos.buscar(estado="sp")
        assert result == {"encargos": []}


class TestIndicadores:
    @patch("sinapi_client.http_client.requests.get")
    def test_listar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"indicadores": {}})
        client = Client(api_key="k")
        result = client.indicadores.listar(indicadores="incc,ipca")
        assert result == {"indicadores": {}}


class TestEstados:
    @patch("sinapi_client.http_client.requests.get")
    def test_listar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"estados": []})
        client = Client(api_key="k")
        result = client.estados.listar(estado="sp")
        assert result == {"estados": []}


class TestOrcamento:
    @patch("sinapi_client.http_client.requests.get")
    def test_gerar(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"total": 100.0})
        client = Client(api_key="k")
        result = client.orcamento.gerar(
            itens="C:12321@3.2,I:234@12.5",
            estado="sp",
            regime="DESONERADO",
        )
        assert result == {"total": 100.0}
