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

    def test_root_has_documentacao(self):
        resp = client.get("/")
        data = resp.json()
        assert data["documentacao"] == "/api/docs"

    def test_root_versao_format(self):
        resp = client.get("/")
        data = resp.json()
        assert data["versao"] == "1.0.0"


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

    def test_buscar_paginacao_pagina2(self):
        resp = client.get("/insumos/buscar", params={"limit": 3, "page": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resultados"]) <= 3
        assert data["page"] == 2

    def test_buscar_com_estado(self):
        resp = client.get("/insumos/buscar", params={"codigo": 370, "estado": "rj"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["resultados"][0]["estado"] == "rj"
        assert data["resultados"][0]["preco"] == 82.30

    def test_buscar_nome_parcial(self):
        resp = client.get("/insumos/buscar", params={"nome": "aco"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_buscar_nome_inexistente(self):
        resp = client.get("/insumos/buscar", params={"nome": "xyzinexistente"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["resultados"] == []

    def test_buscar_codigo_inexistente(self):
        resp = client.get("/insumos/buscar", params={"codigo": 99999})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_buscar_sort_por_preco(self):
        resp = client.get("/insumos/buscar", params={"sort": "preco", "order": "asc"})
        assert resp.status_code == 200
        data = resp.json()
        precos = [r["preco"] for r in data["resultados"]]
        assert precos == sorted(precos)

    def test_buscar_sort_por_preco_desc(self):
        resp = client.get("/insumos/buscar", params={"sort": "preco", "order": "desc"})
        assert resp.status_code == 200
        data = resp.json()
        precos = [r["preco"] for r in data["resultados"]]
        assert precos == sorted(precos, reverse=True)

    def test_buscar_sort_por_codigo(self):
        resp = client.get("/insumos/buscar", params={"sort": "codigo", "order": "asc"})
        assert resp.status_code == 200
        data = resp.json()
        codigos = [r["codigo"] for r in data["resultados"]]
        assert codigos == sorted(codigos)

    def test_buscar_retorna_campos_esperados(self):
        resp = client.get("/insumos/buscar", params={"codigo": 370})
        assert resp.status_code == 200
        item = resp.json()["resultados"][0]
        assert "codigo" in item
        assert "nome" in item
        assert "unidade" in item
        assert "preco" in item
        assert "estado" in item
        assert "referencia" in item

    def test_historico(self):
        resp = client.get("/insumos/historico", params={"codigo": 370, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 370
        assert len(data["historico"]) > 0

    def test_historico_rj(self):
        resp = client.get("/insumos/historico", params={"codigo": 370, "estado": "rj"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "rj"
        assert len(data["historico"]) == 7

    def test_historico_cimento(self):
        resp = client.get("/insumos/historico", params={"codigo": 1379, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 1379
        assert len(data["historico"]) == 7

    def test_historico_nao_encontrado(self):
        resp = client.get("/insumos/historico", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_historico_precos_crescentes(self):
        resp = client.get("/insumos/historico", params={"codigo": 370, "estado": "sp"})
        data = resp.json()
        precos = [h["preco"] for h in data["historico"]]
        assert precos == sorted(precos)

    def test_comparar(self):
        resp = client.get("/insumos/comparar", params={"codigo": 370, "estados": "sp,rj,pb"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparacao"]) == 3

    def test_comparar_nao_encontrado(self):
        resp = client.get("/insumos/comparar", params={"codigo": 99999, "estados": "sp"})
        assert resp.status_code == 404

    def test_comparar_dois_estados(self):
        resp = client.get("/insumos/comparar", params={"codigo": 370, "estados": "sp,rj"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparacao"]) == 2
        estados = [c["estado"] for c in data["comparacao"]]
        assert "sp" in estados
        assert "rj" in estados

    def test_comparar_retorna_nome(self):
        resp = client.get("/insumos/comparar", params={"codigo": 370, "estados": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert "nome" in data
        assert "unidade" in data

    def test_comparar_estado_sem_preco(self):
        resp = client.get("/insumos/comparar", params={"codigo": 370, "estados": "ac"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparacao"]) == 0

    def test_previsao(self):
        resp = client.get("/insumos/previsao", params={"codigo": 370, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert "previsao" in data
        assert len(data["previsao"]) == 6

    def test_previsao_nao_encontrado(self):
        resp = client.get("/insumos/previsao", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_previsao_retorna_preco_atual(self):
        resp = client.get("/insumos/previsao", params={"codigo": 370, "estado": "sp"})
        data = resp.json()
        assert data["preco_atual"] == 75.50
        assert data["codigo"] == 370
        assert data["estado"] == "sp"

    def test_previsao_precos_crescentes(self):
        resp = client.get("/insumos/previsao", params={"codigo": 370, "estado": "sp"})
        data = resp.json()
        precos = [p["preco_previsto"] for p in data["previsao"]]
        assert precos == sorted(precos)

    def test_previsao_estado_invalido(self):
        resp = client.get("/insumos/previsao", params={"codigo": 370, "estado": "xx"})
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

    def test_buscar_por_codigo(self):
        resp = client.get("/composicoes/buscar", params={"codigo": 87316})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["resultados"][0]["codigo"] == 87316

    def test_buscar_nome_inexistente(self):
        resp = client.get("/composicoes/buscar", params={"nome": "xyzinexistente"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_buscar_com_estado_rj(self):
        resp = client.get("/composicoes/buscar", params={"codigo": 87316, "estado": "rj"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["resultados"][0]["estado"] == "rj"
        assert data["resultados"][0]["preco"] == 450.20

    def test_buscar_paginacao(self):
        resp = client.get("/composicoes/buscar", params={"limit": 2, "page": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resultados"]) <= 2

    def test_buscar_sort_preco(self):
        resp = client.get("/composicoes/buscar", params={"sort": "preco", "order": "asc"})
        assert resp.status_code == 200
        data = resp.json()
        precos = [r["preco"] for r in data["resultados"]]
        assert precos == sorted(precos)

    def test_detalhar(self):
        resp = client.get("/composicoes/detalhar", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == 87316
        assert "componentes" in data

    def test_detalhar_nao_encontrada(self):
        resp = client.get("/composicoes/detalhar", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_detalhar_retorna_componentes(self):
        resp = client.get("/composicoes/detalhar", params={"codigo": 87316, "estado": "sp"})
        data = resp.json()
        assert len(data["componentes"]) > 0
        comp = data["componentes"][0]
        assert "codigo" in comp
        assert "nome" in comp
        assert "unidade" in comp
        assert "coeficiente" in comp
        assert "preco_unitario" in comp

    def test_detalhar_estado_invalido(self):
        resp = client.get("/composicoes/detalhar", params={"codigo": 87316, "estado": "xx"})
        assert resp.status_code == 404

    def test_explode(self):
        resp = client.get("/composicoes/explode", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert "insumos" in data
        assert len(data["insumos"]) > 0

    def test_explode_nao_encontrada(self):
        resp = client.get("/composicoes/explode", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_explode_retorna_campos(self):
        resp = client.get("/composicoes/explode", params={"codigo": 87316, "estado": "sp"})
        data = resp.json()
        ins = data["insumos"][0]
        assert "codigo" in ins
        assert "nome" in ins
        assert "coeficiente" in ins
        assert "preco_unitario" in ins
        assert "preco_total" in ins

    def test_explode_sort_preco_total(self):
        resp = client.get(
            "/composicoes/explode",
            params={"codigo": 87316, "estado": "sp", "sort": "preco_total", "order": "desc"},
        )
        assert resp.status_code == 200
        data = resp.json()
        precos = [i["preco_total"] for i in data["insumos"]]
        assert precos == sorted(precos, reverse=True)

    def test_historico(self):
        resp = client.get("/composicoes/historico", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["historico"]) > 0

    def test_historico_nao_encontrada(self):
        resp = client.get("/composicoes/historico", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_historico_precos_crescentes(self):
        resp = client.get("/composicoes/historico", params={"codigo": 87316, "estado": "sp"})
        data = resp.json()
        precos = [h["preco"] for h in data["historico"]]
        assert precos == sorted(precos)

    def test_comparar(self):
        resp = client.get("/composicoes/comparar", params={"codigo": 87316, "estados": "sp,rj"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparacao"]) == 2

    def test_comparar_nao_encontrada(self):
        resp = client.get("/composicoes/comparar", params={"codigo": 99999, "estados": "sp"})
        assert resp.status_code == 404

    def test_comparar_tres_estados(self):
        resp = client.get(
            "/composicoes/comparar", params={"codigo": 87316, "estados": "sp,rj,mg"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comparacao"]) == 3

    def test_previsao(self):
        resp = client.get("/composicoes/previsao", params={"codigo": 87316, "estado": "sp"})
        assert resp.status_code == 200
        data = resp.json()
        assert "previsao" in data

    def test_previsao_nao_encontrada(self):
        resp = client.get("/composicoes/previsao", params={"codigo": 99999, "estado": "sp"})
        assert resp.status_code == 404

    def test_previsao_seis_meses(self):
        resp = client.get("/composicoes/previsao", params={"codigo": 87316, "estado": "sp"})
        data = resp.json()
        assert len(data["previsao"]) == 6

    def test_previsao_preco_atual(self):
        resp = client.get("/composicoes/previsao", params={"codigo": 87316, "estado": "sp"})
        data = resp.json()
        assert data["preco_atual"] == 425.80

    def test_previsao_estado_invalido(self):
        resp = client.get("/composicoes/previsao", params={"codigo": 87316, "estado": "xx"})
        assert resp.status_code == 404


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

    def test_gerar_composicao_inexistente(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "C:99999@1", "estado": "sp"},
        )
        assert resp.status_code == 404

    def test_gerar_tipo_invalido(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "X:370@1", "estado": "sp"},
        )
        assert resp.status_code == 400

    def test_gerar_somente_insumo(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "I:370@10", "estado": "sp"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["itens"]) == 1
        assert data["itens"][0]["tipo"] == "insumo"
        assert data["itens"][0]["quantidade"] == 10.0
        assert data["subtotal"] == round(75.50 * 10, 2)

    def test_gerar_somente_composicao(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "C:87316@2", "estado": "sp"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["itens"]) == 1
        assert data["itens"][0]["tipo"] == "composicao"
        assert data["subtotal"] == round(425.80 * 2, 2)

    def test_gerar_bdi_calculo(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "I:370@10", "estado": "sp", "bdi": 30},
        )
        assert resp.status_code == 200
        data = resp.json()
        subtotal = round(75.50 * 10, 2)
        bdi_valor = round(subtotal * 30 / 100, 2)
        assert data["subtotal"] == subtotal
        assert data["bdi_valor"] == bdi_valor
        assert data["total"] == round(subtotal + bdi_valor, 2)

    def test_gerar_sem_bdi(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "I:370@1", "estado": "sp"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["subtotal"] == data["total"]

    def test_gerar_multiplos_itens(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "I:370@1,I:1379@100,C:87316@2", "estado": "sp"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["itens"]) == 3

    def test_gerar_estado_diferente(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "I:370@1", "estado": "rj"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "rj"
        assert data["itens"][0]["preco_unitario"] == 82.30

    def test_gerar_retorna_campos_item(self):
        resp = client.get(
            "/orcamento/gerar",
            params={"itens": "I:370@1", "estado": "sp"},
        )
        data = resp.json()
        item = data["itens"][0]
        assert "tipo" in item
        assert "codigo" in item
        assert "nome" in item
        assert "unidade" in item
        assert "preco_unitario" in item
        assert "quantidade" in item
        assert "preco_total" in item


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

    def test_listar_por_ibge(self):
        resp = client.get("/estados/listar", params={"ibge": 35})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["estados"][0]["sigla"] == "sp"

    def test_listar_regiao_norte(self):
        resp = client.get("/estados/listar", params={"regiao": "norte"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 7

    def test_listar_regiao_nordeste(self):
        resp = client.get("/estados/listar", params={"regiao": "nordeste"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 9

    def test_listar_regiao_sul(self):
        resp = client.get("/estados/listar", params={"regiao": "sul"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3

    def test_listar_regiao_centro_oeste(self):
        resp = client.get("/estados/listar", params={"regiao": "centro-oeste"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 4

    def test_listar_sigla_inexistente(self):
        resp = client.get("/estados/listar", params={"estado": "xx"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_listar_retorna_campos(self):
        resp = client.get("/estados/listar", params={"estado": "sp"})
        data = resp.json()
        estado = data["estados"][0]
        assert "nome" in estado
        assert "sigla" in estado
        assert "ibge" in estado
        assert "regiao" in estado


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

    def test_listar_um_indicador(self):
        resp = client.get("/indicadores/listar", params={"indicadores": "incc"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["indicadores"][0]["nome"] == "incc"

    def test_listar_indicador_inexistente(self):
        resp = client.get("/indicadores/listar", params={"indicadores": "xyz"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_listar_retorna_campos(self):
        resp = client.get("/indicadores/listar", params={"indicadores": "selic"})
        data = resp.json()
        ind = data["indicadores"][0]
        assert "nome" in ind
        assert "valor" in ind
        assert "referencia" in ind

    def test_listar_valores_esperados(self):
        resp = client.get("/indicadores/listar", params={"indicadores": "selic"})
        data = resp.json()
        assert data["indicadores"][0]["valor"] == 13.25

    def test_listar_dolar(self):
        resp = client.get("/indicadores/listar", params={"indicadores": "dolar"})
        data = resp.json()
        assert data["indicadores"][0]["valor"] == 5.85


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

    def test_buscar_rj(self):
        resp = client.get("/encargos/buscar", params={"estado": "rj"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "rj"
        assert data["horista"] == 119.50

    def test_buscar_mg(self):
        resp = client.get("/encargos/buscar", params={"estado": "mg"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mensalista"] == 83.60

    def test_buscar_retorna_referencia(self):
        resp = client.get("/encargos/buscar", params={"estado": "sp"})
        data = resp.json()
        assert "referencia" in data
        assert data["referencia"] == "2025-01-01"

    def test_buscar_valores_sp(self):
        resp = client.get("/encargos/buscar", params={"estado": "sp"})
        data = resp.json()
        assert data["horista"] == 118.73
        assert data["mensalista"] == 84.95
