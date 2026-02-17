import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Root ───────────────────────────────────────────────────────────────
class TestRoot:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["api"] == "API SINAPI"
        assert "versao" in data


# ── Insumos ────────────────────────────────────────────────────────────
class TestInsumos:
    def test_buscar_todos(self):
        resp = client.get("/insumos/buscar")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "resultados" in data
        assert data["total"] > 0

    def test_buscar_por_nome(self):
        resp = client.get("/insumos/buscar", params={"nome": "cimento"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert "cimento" in data["resultados"][0]["nome"].lower()

    def test_buscar_por_codigo(self):
        resp = client.get("/insumos/buscar", params={"codigo": 370})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["resultados"][0]["codigo"] == 370

    def test_buscar_paginacao(self):
        resp = client.get("/insumos/buscar", params={"limit": 3, "page": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resultados"]) <= 3

    def test_historico(self):
        resp = client.get("/insumos/historico", params={"codigo": 370, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 370
        assert len(data["historico"]) > 0

    def test_historico_nao_encontrado(self):
        resp = client.get("/insumos/historico", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_comparar(self):
        resp = client.get("/insumos/comparar", params={"codigo": 370, "estados": "sp,rj,pb"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparacao"]) == 3

    def test_comparar_nao_encontrado(self):
        resp = client.get("/insumos/comparar", params={"codigo": 99999, "estados": "sp"})
        assert resp.status_code == 404

    def test_previsao(self):
        resp = client.get("/insumos/previsao", params={"codigo": 370, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert "previsao" in data
        assert len(data["previsao"]) == 6

    def test_previsao_nao_encontrado(self):
        resp = client.get("/insumos/previsao", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404


# ── Composições ────────────────────────────────────────────────────────
class TestComposicoes:
    def test_buscar_todos(self):
        resp = client.get("/composicoes/buscar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0

    def test_buscar_por_nome(self):
        resp = client.get("/composicoes/buscar", params={"nome": "argamassa"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_detalhar(self):
        resp = client.get("/composicoes/detalhar", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 87316
        assert "componentes" in data

    def test_detalhar_nao_encontrada(self):
        resp = client.get("/composicoes/detalhar", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_explode(self):
        resp = client.get("/composicoes/explode", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert "insumos" in data
        assert len(data["insumos"]) > 0

    def test_historico(self):
        resp = client.get("/composicoes/historico", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["historico"]) > 0

    def test_comparar(self):
        resp = client.get("/composicoes/comparar", params={"codigo": 87316, "estados": "sp,rj"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparacao"]) == 2

    def test_previsao(self):
        resp = client.get("/composicoes/previsao", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert "previsao" in data


# ── Orçamento ──────────────────────────────────────────────────────────
class TestOrcamento:
    def test_gerar(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "C:87316@3.2,I:370@12.5", "estado": "sp"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["itens"]) == 2
        assert data["subtotal"] > 0

    def test_gerar_com_bdi(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "C:87316@1", "estado": "sp", "bdi": 25},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["bdi_percentual"] == 25.0
        assert data["total"] > data["subtotal"]

    def test_gerar_item_invalido(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "INVALIDO", "estado": "sp"},
        )
        assert resp.status_code == 400

    def test_gerar_insumo_inexistente(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "I:99999@1", "estado": "sp"},
        )
        assert resp.status_code == 404


# ── Estados ────────────────────────────────────────────────────────────
class TestEstados:
    def test_listar_todos(self):
        resp = client.get("/estados/listar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 27

    def test_listar_por_regiao(self):
        resp = client.get("/estados/listar", params={"regiao": "sudeste"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 4

    def test_listar_por_sigla(self):
        resp = client.get("/estados/listar", params={"estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["estados"][0]["sigla"] == "sp"


# ── Indicadores ────────────────────────────────────────────────────────
class TestIndicadores:
    def test_listar_todos(self):
        resp = client.get("/indicadores/listar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 6

    def test_listar_filtrado(self):
        resp = client.get("/indicadores/listar", params={"indicadores": "selic,dolar"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2


# ── Encargos ───────────────────────────────────────────────────────────
class TestEncargos:
    def test_buscar(self):
        resp = client.get("/encargos/buscar", params={"estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "sp"
        assert "horista" in data
        assert "mensalista" in data

    def test_buscar_nao_encontrado(self):
        resp = client.get("/encargos/buscar", params={"estado": "xx"})
        assert resp.status_code == 404
