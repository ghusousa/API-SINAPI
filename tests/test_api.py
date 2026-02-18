"""Testes para os endpoints da API SINAPI."""

import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from api.app import app
from api.deps import API_KEYS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _setup_keys():
    """Configura chave de API válida para os testes."""
    API_KEYS.clear()
    API_KEYS.add("test-key")
    yield
    API_KEYS.clear()


@pytest.fixture
def headers():
    return {"X-API-Key": "test-key"}


# Helper to create a mock httpx.Response
def _mock_upstream(status_code=200, json_data=None):
    """Retorna um patch que simula a resposta da API upstream."""
    from unittest.mock import MagicMock

    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data if json_data is not None else {}
    resp.text = ""

    async def _mock_get(*args, **kwargs):
        return resp

    return _mock_get


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class TestAuth:
    @pytest.mark.anyio
    async def test_missing_api_key(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/estados")
        assert resp.status_code == 401

    @pytest.mark.anyio
    async def test_invalid_api_key(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/estados", headers={"X-API-Key": "wrong"})
        assert resp.status_code == 401

    @pytest.mark.anyio
    async def test_valid_api_key(self):
        with patch("api.proxy.UPSTREAM_API_KEY", "upstream-key"), \
             patch("api.proxy.httpx.AsyncClient") as MockClient:
            mock_inst = AsyncMock()
            from unittest.mock import MagicMock
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"estados": []}
            mock_inst.get.return_value = mock_resp
            mock_inst.__aenter__ = AsyncMock(return_value=mock_inst)
            mock_inst.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_inst

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get("/estados", headers={"X-API-Key": "test-key"})
            assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

class TestEndpoints:
    """Testa que cada endpoint está registrado e faz proxy corretamente."""

    @pytest.mark.anyio
    @pytest.mark.parametrize("path,query", [
        ("/insumos", "nome=cimento&estado=sp"),
        ("/composicoes", "nome=argamassa"),
        ("/composicao", "codigo=123456&estado=sp"),
        ("/composicao_explode", "codigo=123456&estado=sp"),
        ("/historico", "codigo=123&item=insumo&estado=sp"),
        ("/comparar", "codigo=123&item=insumo&estados=sp,rj"),
        ("/previsao", "codigo=123&item=insumo&estado=sp"),
        ("/encargos", "estado=sp"),
        ("/indicadores", "indicadores=incc,ipca"),
        ("/estados", "estado=sp"),
        ("/orcamento", "itens=C:123@1&estado=sp&regime=DESONERADO"),
    ])
    async def test_endpoint_proxies(self, path, query, headers):
        with patch("api.proxy.UPSTREAM_API_KEY", "upstream-key"), \
             patch("api.proxy.httpx.AsyncClient") as MockClient:
            mock_inst = AsyncMock()
            from unittest.mock import MagicMock
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"ok": True}
            mock_inst.get.return_value = mock_resp
            mock_inst.__aenter__ = AsyncMock(return_value=mock_inst)
            mock_inst.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_inst

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(f"{path}?{query}", headers=headers)

            assert resp.status_code == 200
            assert resp.json() == {"ok": True}

            # Verify upstream call was made with correct path
            call_args = mock_inst.get.call_args
            called_url = call_args[1].get("url", call_args[0][0] if call_args[0] else "")
            assert path in str(called_url)

    @pytest.mark.anyio
    async def test_upstream_error_forwarded(self, headers):
        with patch("api.proxy.UPSTREAM_API_KEY", "upstream-key"), \
             patch("api.proxy.httpx.AsyncClient") as MockClient:
            mock_inst = AsyncMock()
            from unittest.mock import MagicMock
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_resp.json.return_value = {"erro": "Não encontrado"}
            mock_resp.text = ""
            mock_inst.get.return_value = mock_resp
            mock_inst.__aenter__ = AsyncMock(return_value=mock_inst)
            mock_inst.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_inst

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get("/insumos?nome=xyz", headers=headers)

            assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_missing_upstream_key(self, headers):
        with patch("api.proxy.UPSTREAM_API_KEY", ""):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get("/estados", headers=headers)
            assert resp.status_code == 500
