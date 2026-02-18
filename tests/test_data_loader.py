"""Testes para o carregador de dados SINAPI (data_loader)."""

import io
import zipfile

import pytest

from api.data_loader import (
    load_xlsx_file,
    load_zip_file,
    _detect_estado_from_filename,
    _detect_referencia_from_filename,
    _detect_regime,
    _detect_sheet_type,
)
from tests.sample_data import create_sample_sinapi_xlsx, create_sample_sinapi_zip


# ---------------------------------------------------------------------------
# Detecção de metadados
# ---------------------------------------------------------------------------

class TestDetectEstado:
    def test_detecta_sp(self):
        assert _detect_estado_from_filename("SINAPI_Preco_Ref_SP_202601.xlsx") == "SP"

    def test_detecta_rj(self):
        assert _detect_estado_from_filename("SINAPI_Preco_Ref_RJ_202601.xlsx") == "RJ"

    def test_nao_detecta(self):
        assert _detect_estado_from_filename("arquivo_generico.xlsx") is None


class TestDetectReferencia:
    def test_formato_hifen(self):
        assert _detect_referencia_from_filename("SINAPI-2026-01-formato.zip") == "2026-01"

    def test_formato_junto(self):
        assert _detect_referencia_from_filename("SINAPI_Preco_202601.xlsx") == "2026-01"

    def test_formato_underscore(self):
        assert _detect_referencia_from_filename("dados_2026_01.xlsx") == "2026-01"

    def test_nao_detecta(self):
        assert _detect_referencia_from_filename("arquivo.xlsx") is None


class TestDetectRegime:
    def test_desonerado(self):
        assert _detect_regime("Insumos Com Desoneração") == "DESONERADO"

    def test_nao_desonerado_sem(self):
        assert _detect_regime("Insumos Sem Desoneração") == "NAO_DESONERADO"

    def test_nao_desonerado_nao(self):
        assert _detect_regime("Insumos Não Desonerado") == "NAO_DESONERADO"

    def test_sigla_icd(self):
        assert _detect_regime("ICD") == "DESONERADO"

    def test_sigla_isd(self):
        assert _detect_regime("ISD") == "NAO_DESONERADO"


class TestDetectSheetType:
    def test_insumo(self):
        assert _detect_sheet_type("Insumos Sem Desoneração") == "insumo"

    def test_composicao(self):
        assert _detect_sheet_type("Composições Com Desoneração") == "composicao"

    def test_analitico(self):
        assert _detect_sheet_type("Composição Analítica") == "analitico"

    def test_desconhecido(self):
        assert _detect_sheet_type("Outra Aba") is None


# ---------------------------------------------------------------------------
# Carregamento XLSX
# ---------------------------------------------------------------------------

class TestLoadXlsx:
    def test_carrega_insumos(self):
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        assert len(data["insumos"]) > 0

    def test_insumo_tem_campos(self):
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        insumo = data["insumos"][0]
        assert "codigo" in insumo
        assert "descricao" in insumo
        assert "unidade" in insumo
        assert "preco_mediano" in insumo
        assert "estado" in insumo
        assert "regime" in insumo
        assert "referencia" in insumo

    def test_carrega_composicoes(self):
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        assert len(data["composicoes"]) > 0

    def test_composicao_tem_campos(self):
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        comp = data["composicoes"][0]
        assert "codigo" in comp
        assert "descricao" in comp
        assert "unidade" in comp
        assert "custo_total" in comp

    def test_carrega_analitico(self):
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        assert len(data["analitico"]) > 0

    def test_analitico_tem_campos(self):
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        item = data["analitico"][0]
        assert "composicao_codigo" in item
        assert "item_codigo" in item
        assert "coeficiente" in item

    def test_dois_regimes(self):
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        regimes = {i["regime"] for i in data["insumos"]}
        assert "DESONERADO" in regimes
        assert "NAO_DESONERADO" in regimes

    def test_estado_correto(self):
        xlsx = create_sample_sinapi_xlsx(estado="RJ", referencia="2025-12")
        data = load_xlsx_file(xlsx, "RJ", "2025-12")
        for insumo in data["insumos"]:
            assert insumo["estado"] == "RJ"
            assert insumo["referencia"] == "2025-12"


# ---------------------------------------------------------------------------
# Carregamento ZIP
# ---------------------------------------------------------------------------

class TestLoadZip:
    def test_carrega_multiplos_estados(self):
        zipbuf = create_sample_sinapi_zip(estados=["SP", "RJ"])
        data = load_zip_file(zipbuf)
        estados = {i["estado"] for i in data["insumos"]}
        assert "SP" in estados
        assert "RJ" in estados

    def test_dados_combinados(self):
        zipbuf = create_sample_sinapi_zip(estados=["SP", "RJ"])
        data = load_zip_file(zipbuf)
        # Deve ter dados de ambos estados
        assert len(data["insumos"]) >= 8  # 4 insumos * 2 regimes = 8 por estado

    def test_ignora_nao_xlsx(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("leiame.txt", "arquivo texto")
        buf.seek(0)
        data = load_zip_file(buf)
        assert len(data["insumos"]) == 0
