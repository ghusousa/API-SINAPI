"""Utilitário para gerar planilhas SINAPI de teste no formato da Caixa."""

import io
import zipfile

from openpyxl import Workbook


# Linhas de metadado que a Caixa insere antes do cabeçalho real
_META_ROWS = [
    ["SINAPI - Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil"],
    ["Caixa Econômica Federal"],
    ["Referência: Janeiro/2026"],
    ["Estado: São Paulo"],
    [""],
    [""],
]


def create_sample_sinapi_xlsx(
    estado: str = "SP",
    referencia: str = "2026-01",
) -> io.BytesIO:
    """Cria uma planilha XLSX SINAPI de amostra para testes.

    Gera dados realistas com abas de insumos (desonerado e não desonerado),
    composições e analítico, simulando o formato oficial da Caixa.
    Inclui linhas de metadado antes do cabeçalho, como no arquivo real.

    Returns:
        BytesIO com o conteúdo do XLSX.
    """
    wb = Workbook()

    # ---- Aba: Insumos Não Desonerado ----
    ws_ins = wb.active
    ws_ins.title = "Insumos Sem Desoneração"
    for meta in _META_ROWS:
        ws_ins.append(meta)
    ws_ins.append(["CODIGO", "DESCRICAO DO INSUMO", "UNIDADE", "PRECO MEDIANO"])
    ws_ins.append([370, "CIMENTO PORTLAND COMPOSTO CP II-32", "KG", 0.62])
    ws_ins.append([1379, "AREIA MEDIA - POSTO JAZIDA/FORNECEDOR", "M3", 72.50])
    ws_ins.append([4750, "PEDREIRO COM ENCARGOS COMPLEMENTARES", "H", 21.05])
    ws_ins.append([43, "CHAPA DE ACO GROSSA, E = 1\"", "KG", 8.12])

    # ---- Aba: Insumos Desonerado ----
    ws_ins_d = wb.create_sheet("Insumos Com Desoneração")
    for meta in _META_ROWS:
        ws_ins_d.append(meta)
    ws_ins_d.append(["CODIGO", "DESCRICAO DO INSUMO", "UNIDADE", "PRECO MEDIANO"])
    ws_ins_d.append([370, "CIMENTO PORTLAND COMPOSTO CP II-32", "KG", 0.60])
    ws_ins_d.append([1379, "AREIA MEDIA - POSTO JAZIDA/FORNECEDOR", "M3", 70.00])
    ws_ins_d.append([4750, "PEDREIRO COM ENCARGOS COMPLEMENTARES", "H", 18.35])
    ws_ins_d.append([43, "CHAPA DE ACO GROSSA, E = 1\"", "KG", 7.95])

    # ---- Aba: Composições Não Desonerado ----
    ws_comp = wb.create_sheet("Composições Sem Desoneração")
    for meta in _META_ROWS:
        ws_comp.append(meta)
    ws_comp.append(["CODIGO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "CUSTO TOTAL"])
    ws_comp.append([87316, "ARGAMASSA TRACO 1:2:8 PREPARO MANUAL", "M3", 501.78])
    ws_comp.append([94964, "CONTRAPISO EM ARGAMASSA TRACO 1:4", "M2", 42.59])
    ws_comp.append([92263, "ALVENARIA DE BLOCOS CERAMICOS", "M2", 68.31])

    # ---- Aba: Composições Desonerado ----
    ws_comp_d = wb.create_sheet("Composições Com Desoneração")
    for meta in _META_ROWS:
        ws_comp_d.append(meta)
    ws_comp_d.append(["CODIGO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "CUSTO TOTAL"])
    ws_comp_d.append([87316, "ARGAMASSA TRACO 1:2:8 PREPARO MANUAL", "M3", 478.20])
    ws_comp_d.append([94964, "CONTRAPISO EM ARGAMASSA TRACO 1:4", "M2", 40.11])
    ws_comp_d.append([92263, "ALVENARIA DE BLOCOS CERAMICOS", "M2", 64.55])

    # ---- Aba: Analítico ----
    ws_ana = wb.create_sheet("Composição Analítica")
    for meta in _META_ROWS:
        ws_ana.append(meta)
    ws_ana.append(["COMPOSICAO", "ITEM CODIGO", "TIPO", "DESCRICAO", "UNIDADE", "COEFICIENTE", "PRECO UNITARIO"])
    # Composição 87316
    ws_ana.append([87316, None, None, None, None, None, None])  # Header da composição
    ws_ana.append([87316, 370, "INSUMO", "CIMENTO PORTLAND COMPOSTO CP II-32", "KG", 216.00, 0.62])
    ws_ana.append([87316, 1379, "INSUMO", "AREIA MEDIA", "M3", 1.14, 72.50])
    ws_ana.append([87316, 4750, "INSUMO", "PEDREIRO", "H", 3.00, 21.05])
    # Composição 94964
    ws_ana.append([94964, None, None, None, None, None, None])
    ws_ana.append([94964, 370, "INSUMO", "CIMENTO PORTLAND", "KG", 10.80, 0.62])
    ws_ana.append([94964, 1379, "INSUMO", "AREIA MEDIA", "M3", 0.03, 72.50])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def create_sample_sinapi_zip(
    estados: list = None,
    referencia: str = "2026-01",
) -> io.BytesIO:
    """Cria um arquivo ZIP SINAPI de amostra contendo XLSX por estado.

    Returns:
        BytesIO com o conteúdo do ZIP.
    """
    if estados is None:
        estados = ["SP", "RJ"]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for uf in estados:
            xlsx_buf = create_sample_sinapi_xlsx(estado=uf, referencia=referencia)
            fname = f"SINAPI_Preco_Ref_{uf}_{referencia.replace('-', '')}.xlsx"
            zf.writestr(fname, xlsx_buf.getvalue())

    buf.seek(0)
    return buf


def _create_insumos_xlsx(estado, referencia, regime_label, meta_rows):
    """Cria XLSX de insumos no formato real SINAPI (arquivo separado)."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Dados"
    for meta in meta_rows:
        ws.append(meta)
    ws.append(["CODIGO", "DESCRICAO DO INSUMO", "UNIDADE", "PRECO MEDIANO"])
    ws.append([370, "CIMENTO PORTLAND COMPOSTO CP II-32", "KG", 0.62])
    ws.append([1379, "AREIA MEDIA - POSTO JAZIDA/FORNECEDOR", "M3", 72.50])
    ws.append([4750, "PEDREIRO COM ENCARGOS COMPLEMENTARES", "H", 21.05])
    ws.append([43, "CHAPA DE ACO GROSSA, E = 1\"", "KG", 8.12])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _create_sintetico_xlsx(estado, referencia, regime_label, meta_rows):
    """Cria XLSX de composições sintético no formato real SINAPI."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Dados"
    for meta in meta_rows:
        ws.append(meta)
    ws.append(["CODIGO", "DESCRICAO DA COMPOSICAO", "UNIDADE", "CUSTO TOTAL"])
    ws.append([87316, "ARGAMASSA TRACO 1:2:8 PREPARO MANUAL", "M3", 501.78])
    ws.append([94964, "CONTRAPISO EM ARGAMASSA TRACO 1:4", "M2", 42.59])
    ws.append([92263, "ALVENARIA DE BLOCOS CERAMICOS", "M2", 68.31])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _create_analitico_xlsx(estado, referencia, regime_label, meta_rows):
    """Cria XLSX de composições analítico no formato real SINAPI."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Dados"
    for meta in meta_rows:
        ws.append(meta)
    ws.append(["COMPOSICAO", "ITEM CODIGO", "TIPO", "DESCRICAO", "UNIDADE",
               "COEFICIENTE", "PRECO UNITARIO"])
    ws.append([87316, None, None, None, None, None, None])
    ws.append([87316, 370, "INSUMO", "CIMENTO PORTLAND COMPOSTO CP II-32",
               "KG", 216.00, 0.62])
    ws.append([87316, 1379, "INSUMO", "AREIA MEDIA", "M3", 1.14, 72.50])
    ws.append([87316, 4750, "INSUMO", "PEDREIRO", "H", 3.00, 21.05])
    ws.append([94964, None, None, None, None, None, None])
    ws.append([94964, 370, "INSUMO", "CIMENTO PORTLAND", "KG", 10.80, 0.62])
    ws.append([94964, 1379, "INSUMO", "AREIA MEDIA", "M3", 0.03, 72.50])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def create_sample_sinapi_zip_real(
    estados: list = None,
    referencia: str = "2026-01",
) -> io.BytesIO:
    """Cria um ZIP no formato real da Caixa com pastas por UF/regime.

    Estrutura gerada:
      SINAPI_ref_Insumos_Composicoes_{UF}_{YYYYMM}_NaoDesonerado/
        SINAPI_Preco_Ref_Insumos_{UF}_{YYYYMM}_NaoDesonerado.xlsx
        SINAPI_Custo_Ref_Composicoes_Sintetico_{UF}_{YYYYMM}_NaoDesonerado.xlsx
        SINAPI_Custo_Ref_Composicoes_Analitico_{UF}_{YYYYMM}_NaoDesonerado.xlsx
      SINAPI_ref_Insumos_Composicoes_{UF}_{YYYYMM}_Desonerado/
        ... (mesmos 3 arquivos, com sufixo Desonerado)

    Returns:
        BytesIO com o conteúdo do ZIP.
    """
    if estados is None:
        estados = ["SP", "RJ"]

    ref_compact = referencia.replace("-", "")

    meta_rows = [
        ["SINAPI - Sistema Nacional de Pesquisa de Custos e Índices"],
        ["Caixa Econômica Federal"],
        ["Referência: " + referencia],
        [""],
        [""],
        [""],
    ]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for uf in estados:
            for regime_label in ("NaoDesonerado", "Desonerado"):
                folder = (f"SINAPI_ref_Insumos_Composicoes_{uf}_{ref_compact}"
                          f"_{regime_label}/")

                ins_name = (f"SINAPI_Preco_Ref_Insumos_{uf}_{ref_compact}"
                            f"_{regime_label}.xlsx")
                sin_name = (f"SINAPI_Custo_Ref_Composicoes_Sintetico_{uf}"
                            f"_{ref_compact}_{regime_label}.xlsx")
                ana_name = (f"SINAPI_Custo_Ref_Composicoes_Analitico_{uf}"
                            f"_{ref_compact}_{regime_label}.xlsx")

                zf.writestr(folder + ins_name,
                            _create_insumos_xlsx(uf, referencia, regime_label,
                                                 meta_rows))
                zf.writestr(folder + sin_name,
                            _create_sintetico_xlsx(uf, referencia,
                                                   regime_label, meta_rows))
                zf.writestr(folder + ana_name,
                            _create_analitico_xlsx(uf, referencia,
                                                   regime_label, meta_rows))

    buf.seek(0)
    return buf
