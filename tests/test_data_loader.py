"""Testes para o carregador de dados SINAPI (data_loader)."""

import io
import zipfile

import pytest

from api.data_loader import (
    load_xlsx_file,
    load_zip_file,
    parse_referencia_xlsx,
    _detect_estado_from_filename,
    _detect_referencia_from_filename,
    _detect_regime,
    _detect_sheet_type,
    _detect_file_type_from_filename,
    _is_national_reference_file,
    _extract_hyperlink_value,
    _find_header_row,
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
        assert "nome" in insumo
        assert "unidade" in insumo
        assert "preco" in insumo
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
        assert "nome" in comp
        assert "unidade" in comp
        assert "preco" in comp

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
            assert insumo["referencia"] == "2025-12-01"


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

    def test_hyperlink_semicolon_separator(self):
        """SINAPI em locale brasileiro usa ponto-e-vírgula como separador."""
        result = _extract_hyperlink_value('=HYPERLINK("http://sinapi.caixa.gov.br/370";370)')
        assert result == 370

    def test_hyperlink_semicolon_with_quotes(self):
        result = _extract_hyperlink_value('=HYPERLINK("http://sinapi.caixa.gov.br";"12345")')
        assert result == 12345


# ---------------------------------------------------------------------------
# _find_col: prefere colunas com mais keywords
# ---------------------------------------------------------------------------

class TestFindCol:
    def test_prefers_more_specific_match(self):
        """PRECO MEDIANO deve ganhar de ORIGEM DO PRECO quando keywords são PRECO e MEDIANO."""
        from api.data_loader import _find_col
        columns = {
            "CODIGO": 0,
            "DESCRICAO DO INSUMO": 1,
            "UNIDADE": 2,
            "ORIGEM DO PRECO": 3,
            "PRECO MEDIANO R$": 4,
        }
        result = _find_col(columns, "PRECO", "MEDIANO", "CUSTO")
        assert result == 4  # Must be PRECO MEDIANO, not ORIGEM DO PRECO


# ---------------------------------------------------------------------------
# Parsing com HYPERLINK em CODIGO (formato real Caixa com formulas)
# ---------------------------------------------------------------------------

class TestHyperlinkInCodigo:
    def test_xlsx_with_hyperlink_formulas(self):
        """Arquivos SINAPI reais usam HYPERLINK em CODIGO. Devem ser extraídos."""
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Insumos Sem Desoneração"
        ws.append(["CODIGO", "DESCRICAO DO INSUMO", "UNIDADE", "PRECO MEDIANO"])
        ws.cell(row=2, column=1).value = '=HYPERLINK("http://sinapi.caixa.gov.br/370",370)'
        ws.cell(row=2, column=2).value = "CIMENTO PORTLAND"
        ws.cell(row=2, column=3).value = "KG"
        ws.cell(row=2, column=4).value = 0.62
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        data = load_xlsx_file(buf, "SP", "2026-01")
        assert len(data["insumos"]) == 1
        assert data["insumos"][0]["codigo"] == 370

    def test_real_format_with_origin_and_preco_columns(self):
        """Arquivo com ORIGEM DO PRECO e PRECO MEDIANO deve usar o MEDIANO."""
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Insumos Sem Desoneração"
        ws.append(["CODIGO", "DESCRICAO DO INSUMO", "UNIDADE", "ORIGEM DO PRECO", "PRECO MEDIANO R$"])
        ws.append([370, "CIMENTO PORTLAND", "KG", "CAIXA", 0.62])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        data = load_xlsx_file(buf, "SP", "2026-01")
        assert len(data["insumos"]) == 1
        assert data["insumos"][0]["preco"] == 0.62  # Must be the price, not "CAIXA"


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
        assert "nome" in ins
        assert "unidade" in ins
        assert "preco" in ins
        assert "estado" in ins
        assert "regime" in ins

    def test_composicao_campos(self):
        zipbuf = create_sample_sinapi_zip_real(estados=["SP"])
        data = load_zip_file(zipbuf)
        comp = data["composicoes"][0]
        assert "codigo" in comp
        assert "nome" in comp
        assert "preco" in comp

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


# ---------------------------------------------------------------------------
# Detecção de arquivo nacional
# ---------------------------------------------------------------------------

class TestIsNationalReferenceFile:
    def test_referencia(self):
        assert _is_national_reference_file("SINAPI_Referência_2026_01.xlsx") is True

    def test_mao_de_obra(self):
        assert _is_national_reference_file("SINAPI_mao_de_obra_2026_01.xlsx") is True

    def test_familias(self):
        assert _is_national_reference_file("SINAPI_familias_e_coeficientes_2026_01.xlsx") is True

    def test_insumo_por_estado_nao_e_nacional(self):
        assert _is_national_reference_file("SINAPI_Preco_Ref_Insumos_SP_202601_NaoDesonerado.xlsx") is False

    def test_manutencoes_e_nacional(self):
        # Manutenções é processado como nacional (pode ter colunas UF)
        assert _is_national_reference_file("SINAPI_Manutenções_2026_01.xlsx") is True


# ---------------------------------------------------------------------------
# Formato Nacional de Referência (colunas UF)
# ---------------------------------------------------------------------------

def _create_national_xlsx():
    """Cria XLSX no formato nacional com abas ISD/ICD/CSD/CCD e colunas UF."""
    from openpyxl import Workbook
    wb = Workbook()
    # --- ISD: Insumos Sem Desoneração ---
    ws_isd = wb.active
    ws_isd.title = "ISD"
    # Metadata rows (like the real file has before the header)
    for i in range(8):
        ws_isd.append([f"Metadata row {i + 1}"])
    # Row 9: Header
    ws_isd.append(["CODIGO DO INSUMO", "DESCRICAO DO INSUMO", "UNIDADE", "SP", "RJ", "MG"])
    ws_isd.append([370, "CIMENTO PORTLAND", "KG", 0.62, 0.71, 0.55])
    ws_isd.append([1379, "AREIA MEDIA", "M3", 72.50, 68.90, 75.10])

    # --- ICD: Insumos Com Desoneração ---
    ws_icd = wb.create_sheet("ICD")
    for i in range(8):
        ws_icd.append([f"Metadata row {i + 1}"])
    ws_icd.append(["CODIGO DO INSUMO", "DESCRICAO DO INSUMO", "UNIDADE", "SP", "RJ", "MG"])
    ws_icd.append([370, "CIMENTO PORTLAND", "KG", 0.58, 0.65, 0.50])

    # --- CSD: Composições Sem Desoneração ---
    ws_csd = wb.create_sheet("CSD")
    for i in range(8):
        ws_csd.append([f"Metadata row {i + 1}"])
    ws_csd.append(["CODIGO DA COMPOSICAO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "SP", "RJ", "MG"])
    ws_csd.append([87316, "ARGAMASSA TRACO 1:2:8", "M3", 501.78, 492.50, 510.20])

    # --- CCD: Composições Com Desoneração ---
    ws_ccd = wb.create_sheet("CCD")
    for i in range(8):
        ws_ccd.append([f"Metadata row {i + 1}"])
    ws_ccd.append(["CODIGO DA COMPOSICAO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "SP", "RJ", "MG"])
    ws_ccd.append([87316, "ARGAMASSA TRACO 1:2:8", "M3", 480.12, 471.30, 490.55])

    # Sheet that should be ignored
    ws_other = wb.create_sheet("Informacoes")
    ws_other.append(["Este é um relatório informativo"])

    return wb


class TestParseReferenciaNacional:
    def test_carrega_insumos_por_uf(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        # ISD: 2 insumos * 3 UFs = 6; ICD: 1 insumo * 3 UFs = 3 => total 9
        assert len(data["insumos"]) == 9

    def test_carrega_composicoes_por_uf(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        # CSD: 1 comp * 3 UFs = 3; CCD: 1 comp * 3 UFs = 3 => total 6
        assert len(data["composicoes"]) == 6

    def test_insumo_tem_estado_correto(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        estados = {ins["estado"] for ins in data["insumos"]}
        assert estados == {"SP", "RJ", "MG"}

    def test_insumo_tem_regime_correto(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        regimes = {ins["regime"] for ins in data["insumos"]}
        assert "NAO_DESONERADO" in regimes
        assert "DESONERADO" in regimes

    def test_insumo_preco_correto(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        sp_cimento = [i for i in data["insumos"]
                      if i["codigo"] == 370 and i["estado"] == "SP"
                      and i["regime"] == "NAO_DESONERADO"]
        assert len(sp_cimento) == 1
        assert sp_cimento[0]["preco"] == 0.62

    def test_composicao_custo_correto(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        rj_argamassa = [c for c in data["composicoes"]
                        if c["codigo"] == 87316 and c["estado"] == "RJ"
                        and c["regime"] == "NAO_DESONERADO"]
        assert len(rj_argamassa) == 1
        assert rj_argamassa[0]["preco"] == 492.50

    def test_referencia_preenchida(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        for ins in data["insumos"]:
            assert ins["referencia"] == "2026-01-01"

    def test_ignora_aba_desconhecida(self):
        wb = _create_national_xlsx()
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        # "Informacoes" sheet should not contribute data
        assert data["analitico"] == []


class TestNationalZipFormat:
    """Testa o upload de ZIP no formato nacional de referência."""

    def test_zip_com_referencia(self):
        wb = _create_national_xlsx()
        buf = io.BytesIO()
        wb.save(buf)
        wb.close()
        xlsx_bytes = buf.getvalue()

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            zf.writestr("SINAPI_Referência_2026_01.xlsx", xlsx_bytes)
        zip_buf.seek(0)

        data = load_zip_file(zip_buf)
        assert len(data["insumos"]) > 0
        assert len(data["composicoes"]) > 0

    def test_zip_com_4_arquivos_nacionais(self):
        """Simula o ZIP real com 4 arquivos nacionais."""
        from openpyxl import Workbook

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            # SINAPI_Referência — principal
            wb = _create_national_xlsx()
            buf = io.BytesIO()
            wb.save(buf)
            wb.close()
            zf.writestr("SINAPI_Referência_2026_01.xlsx", buf.getvalue())

            # SINAPI_mao_de_obra — mão de obra por UF
            wb2 = Workbook()
            ws = wb2.active
            ws.title = "Insumos MO"
            for i in range(8):
                ws.append([f"Metadata {i}"])
            ws.append(["CODIGO DO INSUMO", "DESCRICAO DO INSUMO", "UNIDADE", "SP", "RJ"])
            ws.append([99001, "PEDREIRO", "H", 15.50, 14.80])
            buf2 = io.BytesIO()
            wb2.save(buf2)
            wb2.close()
            zf.writestr("SINAPI_mao_de_obra_2026_01.xlsx", buf2.getvalue())

            # SINAPI_familias — famílias de composições
            wb3 = Workbook()
            ws3 = wb3.active
            ws3.title = "Composicoes Familias"
            for i in range(8):
                ws3.append([f"Metadata {i}"])
            ws3.append(["CODIGO DA COMPOSICAO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "SP"])
            ws3.append([90001, "FAMILIA ALVENARIA", "M2", 120.50])
            buf3 = io.BytesIO()
            wb3.save(buf3)
            wb3.close()
            zf.writestr("SINAPI_familias_e_coeficientes_2026_01.xlsx", buf3.getvalue())

            # SINAPI_Manutenções — este não é reconhecido como nacional
            wb4 = Workbook()
            ws4 = wb4.active
            ws4.title = "Manutenções"
            ws4.append(["REFERENCIA", "TIPO", "CODIGO"])
            buf4 = io.BytesIO()
            wb4.save(buf4)
            wb4.close()
            zf.writestr("SINAPI_Manutenções_2026_01.xlsx", buf4.getvalue())

        zip_buf.seek(0)
        data = load_zip_file(zip_buf)

        # Referência: 9 insumos + mao_de_obra: 2 insumos = 11
        assert len(data["insumos"]) == 11
        # Referência: 6 composições + familias: 1 = 7
        assert len(data["composicoes"]) == 7


# ---------------------------------------------------------------------------
# Header detection improvements
# ---------------------------------------------------------------------------

class TestFindHeaderRow:
    """Testa a detecção de cabeçalho com diferentes formatos."""

    def test_header_com_codigo(self):
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["CODIGO", "DESCRICAO", "UNIDADE"])
        ws.append([1, "Item", "KG"])
        row, cols = _find_header_row(ws)
        assert row == 1
        assert "CODIGO" in cols
        wb.close()

    def test_header_com_composicao_e_ufs(self):
        """CSD sem CODIGO mas com COMPOSICAO + colunas UF."""
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["COMPOSICAO", "DESCRICAO", "UNIDADE", "AC", "AL", "SP"])
        ws.append([94214, "ALVENARIA", "M2", 120.0, 125.0, 130.0])
        row, cols = _find_header_row(ws)
        assert row == 1
        assert "COMPOSICAO" in cols
        wb.close()

    def test_header_apos_linhas_vazias(self):
        """Cabeçalho após 7 linhas vazias (não termina prematuramente)."""
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["Metadata"])
        for _ in range(7):
            ws.append([None])
        ws.append(["CODIGO", "DESCRICAO", "UNIDADE"])
        row, cols = _find_header_row(ws)
        assert row == 9
        wb.close()

    def test_header_com_grupo_e_ufs(self):
        """Cabeçalho com GRUPO + UFs."""
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["GRUPO", "SUBGRUPO", "DESCRICAO", "AC", "AL", "SP"])
        row, cols = _find_header_row(ws)
        assert row == 1
        wb.close()


class TestComposicoesSemCodigo:
    """Testa parsing de composições onde header usa COMPOSICAO em vez de CODIGO."""

    def test_csd_com_composicao_header(self):
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "CSD"
        for i in range(5):
            ws.append([f"Metadata {i}"])
        ws.append(["COMPOSICAO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "SP", "RJ", "MG"])
        ws.append([94214, "ALVENARIA DE BLOCO CERAMICO", "M2", 120.0, 125.0, 130.0])
        ws.append([95467, "CONTRAPISO EM ARGAMASSA", "M2", 45.0, 48.0, 50.0])
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        # 2 composições * 3 UFs = 6
        assert len(data["composicoes"]) == 6

    def test_csd_e_isd_juntos(self):
        from openpyxl import Workbook
        wb = Workbook()
        # ISD with CODIGO
        ws_isd = wb.active
        ws_isd.title = "ISD"
        for i in range(5):
            ws_isd.append([f"Metadata {i}"])
        ws_isd.append(["CODIGO DO INSUMO", "DESCRICAO DO INSUMO", "UNIDADE", "SP"])
        ws_isd.append([370, "CIMENTO", "KG", 0.58])

        # CSD with COMPOSICAO (no CODIGO)
        ws_csd = wb.create_sheet("CSD")
        for i in range(5):
            ws_csd.append([f"Metadata {i}"])
        ws_csd.append(["COMPOSICAO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "SP"])
        ws_csd.append([94214, "ALVENARIA", "M2", 120.0])

        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        assert len(data["insumos"]) == 1
        assert len(data["composicoes"]) == 1
        assert data["composicoes"][0]["codigo"] == 94214

    def test_aba_generica_com_composicao_e_ufs(self):
        """Aba com nome genérico mas colunas COMPOSICAO + UFs é detectada."""
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Plan1"
        ws.append(["COMPOSICAO", "DESCRICAO", "UNIDADE", "AC", "AL", "SP", "RJ"])
        ws.append([94214, "ALVENARIA", "M2", 120.0, 125.0, 130.0, 128.0])
        data = parse_referencia_xlsx(wb, "2026-01")
        wb.close()
        # Auto-detected as composicao, 1 row * 4 UFs = 4
        assert len(data["composicoes"]) == 4


class TestDetectSheetTypeExpanded:
    """Testa os novos padrões de detecção de tipo de aba."""

    def test_servico(self):
        assert _detect_sheet_type("Serviços") == "composicao"

    def test_manutencao(self):
        assert _detect_sheet_type("Manutenções") == "composicao"

    def test_manutencao_normalised(self):
        assert _detect_sheet_type("MANUTENCOES") == "composicao"
