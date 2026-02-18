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
    _detect_file_type_from_filename,
    _extract_hyperlink_value,
)
from tests.sample_data import (
    create_sample_sinapi_xlsx,
    create_sample_sinapi_zip,
    create_sample_sinapi_zip_real,
)


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

    def test_filename_nao_desonerado(self):
        assert _detect_regime("SINAPI_ref_Insumos_Composicoes_SP_202601_NaoDesonerado") == "NAO_DESONERADO"

    def test_filename_desonerado(self):
        assert _detect_regime("SINAPI_ref_Insumos_Composicoes_SP_202601_Desonerado") == "DESONERADO"


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


# ---------------------------------------------------------------------------
# Detecção de tipo de arquivo por nome (formato real)
# ---------------------------------------------------------------------------

class TestDetectFileType:
    def test_insumos(self):
        assert _detect_file_type_from_filename(
            "SINAPI_Preco_Ref_Insumos_SP_202601_NaoDesonerado.xlsx"
        ) == "insumo"

    def test_sintetico(self):
        assert _detect_file_type_from_filename(
            "SINAPI_Custo_Ref_Composicoes_Sintetico_SP_202601_NaoDesonerado.xlsx"
        ) == "composicao"

    def test_analitico(self):
        assert _detect_file_type_from_filename(
            "SINAPI_Custo_Ref_Composicoes_Analitico_SP_202601_NaoDesonerado.xlsx"
        ) == "analitico"

    def test_desconhecido(self):
        assert _detect_file_type_from_filename("outro_arquivo.xlsx") is None

    def test_with_path(self):
        assert _detect_file_type_from_filename(
            "SINAPI_ref_Insumos_Composicoes_SP_202601_Desonerado/"
            "SINAPI_Preco_Ref_Insumos_SP_202601_Desonerado.xlsx"
        ) == "insumo"


# ---------------------------------------------------------------------------
# Extração de HYPERLINK
# ---------------------------------------------------------------------------

class TestExtractHyperlink:
    def test_normal_int(self):
        assert _extract_hyperlink_value(370) == 370

    def test_normal_float(self):
        assert _extract_hyperlink_value(370.0) == 370.0

    def test_none(self):
        assert _extract_hyperlink_value(None) is None

    def test_hyperlink_formula(self):
        result = _extract_hyperlink_value('=HYPERLINK("http://example.com", 12345)')
        assert result == 12345

    def test_hyperlink_formula_with_quotes(self):
        result = _extract_hyperlink_value('=HYPERLINK("http://example.com", "67890")')
        assert result == 67890

    def test_plain_string(self):
        assert _extract_hyperlink_value("hello") == "hello"


# ---------------------------------------------------------------------------
# Header row em posição não-padrão
# ---------------------------------------------------------------------------

class TestHeaderRowDetection:
    def test_header_after_metadata(self):
        """Verifica que o header é encontrado mesmo com linhas de metadado antes."""
        xlsx = create_sample_sinapi_xlsx(estado="SP", referencia="2026-01")
        data = load_xlsx_file(xlsx, "SP", "2026-01")
        # Deve encontrar dados mesmo com 6 linhas de metadado antes do header
        assert len(data["insumos"]) > 0
        assert len(data["composicoes"]) > 0
        assert len(data["analitico"]) > 0


# ---------------------------------------------------------------------------
# Carregamento ZIP formato real Caixa
# ---------------------------------------------------------------------------

class TestLoadZipReal:
    def test_carrega_insumos(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        assert len(data["insumos"]) > 0

    def test_carrega_composicoes(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        assert len(data["composicoes"]) > 0

    def test_carrega_analitico(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        assert len(data["analitico"]) > 0

    def test_multiplos_estados(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP", "RJ"])
        data = load_zip_file(zipbuf)
        estados_insumos = {i["estado"] for i in data["insumos"]}
        assert "SP" in estados_insumos
        assert "RJ" in estados_insumos

    def test_dois_regimes(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        regimes = {i["regime"] for i in data["insumos"]}
        assert "DESONERADO" in regimes
        assert "NAO_DESONERADO" in regimes

    def test_regime_nao_desonerado_from_filename(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        nd = [i for i in data["insumos"] if i["regime"] == "NAO_DESONERADO"]
        assert len(nd) == 4  # 4 insumos

    def test_regime_desonerado_from_filename(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        d = [i for i in data["insumos"] if i["regime"] == "DESONERADO"]
        assert len(d) == 4  # 4 insumos

    def test_insumo_campos(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        ins = data["insumos"][0]
        assert "codigo" in ins
        assert "descricao" in ins
        assert "unidade" in ins
        assert "preco_mediano" in ins
        assert "estado" in ins
        assert "regime" in ins

    def test_composicao_campos(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        comp = data["composicoes"][0]
        assert "codigo" in comp
        assert "descricao" in comp
        assert "custo_total" in comp

    def test_analitico_campos(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        ana = data["analitico"][0]
        assert "composicao_codigo" in ana
        assert "item_codigo" in ana
        assert "coeficiente" in ana

    def test_dados_completos_dois_estados(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP", "RJ"])
        data = load_zip_file(zipbuf)
        # 4 insumos * 2 regimes * 2 estados = 16
        assert len(data["insumos"]) == 16
        # 3 composições * 2 regimes * 2 estados = 12
        assert len(data["composicoes"]) == 12
        # 5 itens analíticos * 2 regimes * 2 estados = 20
        assert len(data["analitico"]) == 20
