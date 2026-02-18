"""Testes para os endpoints da API SINAPI."""

import io
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from api.app import app
from api.data_store import store
from tests.sample_data import create_sample_sinapi_xlsx, create_sample_sinapi_zip


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _setup_keys():
    """Configura chave de API válida para os testes."""
    import api.deps
    original = api.deps.API_KEYS
    api.deps.API_KEYS = frozenset({"test-key"})
    yield
    api.deps.API_KEYS = original


@pytest.fixture(autouse=True)
def _load_sample_data():
    """Carrega dados de amostra antes de cada teste."""
    store.clear()
    xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
    from api.data_loader import load_xlsx_file
    data = load_xlsx_file(xlsx, "SP", "2026-01")
    store.load(data)
    yield
    store.clear()


@pytest.fixture
def headers():
    return {"X-API-Key": "test-key"}


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
    async def test_valid_api_key(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/estados", headers=headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

class TestUpload:
    @pytest.mark.anyio
    async def test_upload_xlsx(self):
        xlsx = create_sample_sinapi_xlsx(estado="RJ", referencia="2026-01")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(
                "/upload?estado=RJ&referencia=2026-01",
                files={"file": ("sinapi_rj.xlsx", xlsx.getvalue(), "application/octet-stream")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["insumos"] > 0
        assert data["composicoes"] > 0

    @pytest.mark.anyio
    async def test_upload_zip(self):
        zipbuf = create_sample_sinapi_zip(estados=["SP", "RJ"])
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(
                "/upload",
                files={"file": ("SINAPI-2026-01.zip", zipbuf.getvalue(), "application/octet-stream")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["insumos"] > 0

    @pytest.mark.anyio
    async def test_upload_invalid_format(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(
                "/upload",
                files={"file": ("data.csv", b"a,b,c", "text/csv")},
            )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Insumos
# ---------------------------------------------------------------------------

class TestInsumos:
    @pytest.mark.anyio
    async def test_buscar_por_nome(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/insumos?nome=cimento&estado=sp", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert "CIMENTO" in data["data"][0]["descricao"].upper()

    @pytest.mark.anyio
    async def test_buscar_por_codigo(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/insumos?codigo=370&estado=sp", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert data["data"][0]["codigo"] == 370

    @pytest.mark.anyio
    async def test_buscar_paginacao(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/insumos?estado=sp&limit=2&page=1", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["limit"] == 2
        assert len(data["data"]) <= 2

    @pytest.mark.anyio
    async def test_buscar_por_regime(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(
                "/insumos?codigo=370&estado=sp&regime=DESONERADO",
                headers=headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert data["data"][0]["regime"] == "DESONERADO"


# ---------------------------------------------------------------------------
# Composições
# ---------------------------------------------------------------------------

class TestComposicoes:
    @pytest.mark.anyio
    async def test_buscar_por_nome(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/composicoes?nome=argamassa&estado=sp", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    @pytest.mark.anyio
    async def test_detalhar(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/composicao?codigo=87316&estado=sp", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 87316
        assert "itens" in data

    @pytest.mark.anyio
    async def test_detalhar_not_found(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/composicao?codigo=999999&estado=sp", headers=headers)
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_explode(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/composicao_explode?codigo=87316&estado=sp", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 87316
        assert data["total_itens"] >= 1


# ---------------------------------------------------------------------------
# Histórico / Comparar / Previsão
# ---------------------------------------------------------------------------

class TestHistorico:
    @pytest.mark.anyio
    async def test_historico_insumo(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/historico?codigo=370&item=insumo&estado=sp", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 370
        assert data["item"] == "insumo"

    @pytest.mark.anyio
    async def test_comparar(self, headers):
        # Load RJ data too
        xlsx = create_sample_sinapi_xlsx(estado="RJ", referencia="2026-01")
        from api.data_loader import load_xlsx_file
        data_rj = load_xlsx_file(xlsx, "RJ", "2026-01")
        store.load(data_rj)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/comparar?codigo=370&item=insumo&estados=SP,RJ", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 370
        assert len(data["comparacao"]) >= 2

    @pytest.mark.anyio
    async def test_previsao(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(
                "/previsao?codigo=370&item=insumo&estado=sp&regime=NAO_DESONERADO",
                headers=headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 370
        assert data["previsao"] is not None


# ---------------------------------------------------------------------------
# Encargos, Indicadores, Estados, Orçamento
# ---------------------------------------------------------------------------

class TestEncargos:
    @pytest.mark.anyio
    async def test_buscar(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/encargos?estado=sp", headers=headers)
        assert resp.status_code == 200


class TestIndicadores:
    @pytest.mark.anyio
    async def test_listar(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/indicadores", headers=headers)
        assert resp.status_code == 200


class TestEstados:
    @pytest.mark.anyio
    async def test_listar_todos(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/estados", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["estados"]) == 27  # All Brazilian states

    @pytest.mark.anyio
    async def test_listar_por_uf(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/estados?estado=SP", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["estados"]) == 1
        assert data["estados"][0]["uf"] == "SP"

    @pytest.mark.anyio
    async def test_listar_por_regiao(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/estados?regiao=sudeste", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(e["regiao"] == "sudeste" for e in data["estados"])


class TestOrcamento:
    @pytest.mark.anyio
    async def test_gerar(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(
                "/orcamento?itens=C:87316@2.0,I:370@100&estado=SP&regime=NAO_DESONERADO",
                headers=headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        assert len(data["itens"]) == 2
        assert data["estado"] == "SP"

    @pytest.mark.anyio
    async def test_gerar_com_bdi(self, headers):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(
                "/orcamento?itens=I:370@100&estado=SP&regime=NAO_DESONERADO&bdi=25",
                headers=headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["bdi_percentual"] == 25.0
        assert data["bdi_valor"] > 0
        assert data["total"] > data["subtotal"]
