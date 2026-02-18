"""Rotas da API SINAPI.

Cada endpoint aceita os mesmos query-params da API oficial do Orçamentador
e serve os dados a partir dos arquivos SINAPI carregados localmente.
"""

import io
import logging
import logging.handlers
import os
import re
import zipfile
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from api.data_store import store
from api.data_loader import load_zip_file, load_xlsx_file

router = APIRouter()

DATA_DIR = os.environ.get("SINAPI_DATA_DIR", "data")


# ---- Upload de dados -------------------------------------------------------

@router.post("/upload", tags=["Admin"])
async def upload_sinapi(
    file: UploadFile = File(...),
    estado: Optional[str] = Query(None, description="UF do estado (obrigatório para XLSX avulso)"),
    referencia: Optional[str] = Query(None, description="Referência YYYY-MM (obrigatório para XLSX avulso)"),
):
    """Carrega um arquivo SINAPI (ZIP ou XLSX) no servidor.

    O arquivo é salvo na pasta de dados para ser recarregado automaticamente
    quando o servidor reiniciar.
    """
    contents = await file.read()
    filename = file.filename or ""

    logger = logging.getLogger("api.upload")

    # Capture parsing logs for diagnostic feedback
    log_handler = logging.handlers.MemoryHandler(capacity=200)
    log_formatter = logging.Formatter("%(message)s")
    log_handler.setFormatter(log_formatter)
    data_logger = logging.getLogger("api.data_loader")
    data_logger.addHandler(log_handler)
    data_logger.setLevel(logging.INFO)

    try:
        if filename.lower().endswith(".zip"):
            data = load_zip_file(io.BytesIO(contents))
        elif filename.lower().endswith(".xlsx"):
            if not estado or not referencia:
                raise HTTPException(
                    status_code=400,
                    detail="Para upload de XLSX avulso informe 'estado' e 'referencia'",
                )
            data = load_xlsx_file(io.BytesIO(contents), estado, referencia)
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado. Envie .zip ou .xlsx")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao processar arquivo SINAPI")
        raise HTTPException(
            status_code=422,
            detail=f"Erro ao processar o arquivo: {e}",
        )
    finally:
        data_logger.removeHandler(log_handler)

    # Extract parsing logs for diagnostics
    log_handler.flush()
    parsing_logs = [
        log_formatter.format(record) for record in log_handler.buffer
    ]

    total_records = (
        len(data.get("insumos", []))
        + len(data.get("composicoes", []))
        + len(data.get("analitico", []))
    )
    if total_records == 0:
        # Include diagnostic info + parsing logs
        diag = _diagnose_zip(contents, filename) if filename.lower().endswith(".zip") else ""
        raise HTTPException(
            status_code=422,
            detail=(
                "Nenhum dado encontrado no arquivo. "
                "Verifique se o arquivo é um SINAPI válido da Caixa "
                "(formato XLSX/ZIP com planilhas de Insumos, Composições e Analítico)."
                + (f" Diagnóstico: {diag}" if diag else "")
                + (f" Logs: {parsing_logs}" if parsing_logs else "")
            ),
        )

    store.load(data)

    # Salvar arquivo no diretório de dados para persistência.
    # Sanitizar nome: apenas alfanuméricos, hífens, underscores e ponto.
    safe_name = re.sub(r'[^\w.\-]', '_', os.path.basename(filename))
    if not safe_name:
        safe_name = "upload.dat"
    os.makedirs(DATA_DIR, exist_ok=True)
    save_path = os.path.join(DATA_DIR, safe_name)
    with open(save_path, "wb") as f:
        f.write(contents)

    response = {
        "mensagem": "Dados carregados com sucesso",
        "arquivo_salvo": save_path,
        "insumos": len(data.get("insumos", [])),
        "composicoes": len(data.get("composicoes", [])),
        "analitico": len(data.get("analitico", [])),
    }

    # Add parsing details if some categories are empty
    if not data.get("composicoes") or not data.get("analitico"):
        response["detalhes_parsing"] = parsing_logs

    return response


# ---- Status ----------------------------------------------------------------

@router.get("/status", tags=["Admin"])
async def status():
    """Mostra o status dos dados carregados no servidor."""
    return {
        "insumos_carregados": len(store._insumos),
        "composicoes_carregadas": len(store._composicoes),
        "analitico_carregados": len(store._analitico),
        "estados_disponiveis": sorted(store._estados),
        "referencias_disponiveis": sorted(store._referencias),
        "diretorio_dados": DATA_DIR,
    }


# ---- Insumos ---------------------------------------------------------------

@router.get("/insumos")
async def buscar_insumos(request: Request):
    """Busca insumos por nome, código ou filtros."""
    params = dict(request.query_params)
    # Converter tipos
    if "codigo" in params:
        params["codigo"] = int(params["codigo"])
    if "page" in params:
        params["page"] = int(params["page"])
    if "limit" in params:
        params["limit"] = int(params["limit"])
    return store.buscar_insumos(**params)


# ---- Composições -----------------------------------------------------------

@router.get("/composicoes")
async def buscar_composicoes(request: Request):
    """Busca composições por nome, código ou filtros."""
    params = dict(request.query_params)
    if "codigo" in params:
        params["codigo"] = int(params["codigo"])
    if "page" in params:
        params["page"] = int(params["page"])
    if "limit" in params:
        params["limit"] = int(params["limit"])
    return store.buscar_composicoes(**params)


@router.get("/composicao")
async def detalhar_composicao(
    codigo: int = Query(..., description="Código da composição"),
    estado: Optional[str] = Query(None),
    regime: Optional[str] = Query(None),
):
    """Detalha uma composição específica."""
    result = store.detalhar_composicao(codigo=codigo, estado=estado, regime=regime)
    if result is None:
        raise HTTPException(status_code=404, detail="Composição não encontrada")
    return result


@router.get("/composicao_explode")
async def explode_composicao(
    codigo: int = Query(..., description="Código da composição"),
    estado: Optional[str] = Query(None),
    regime: Optional[str] = Query(None),
):
    """Lista todos os insumos de uma composição (explodir)."""
    return store.explode_composicao(codigo=codigo, estado=estado, regime=regime)


# ---- Histórico / Comparar / Previsão (insumos e composições) ---------------

@router.get("/historico")
async def historico(
    codigo: int = Query(..., description="Código do item"),
    item: str = Query("insumo", description="Tipo: insumo ou composicao"),
    estado: Optional[str] = Query(None),
):
    """Histórico de preços de insumo ou composição."""
    return store.historico(codigo=codigo, item=item, estado=estado)


@router.get("/comparar")
async def comparar(
    codigo: int = Query(..., description="Código do item"),
    item: str = Query("insumo", description="Tipo: insumo ou composicao"),
    estados: Optional[str] = Query(None, description="UFs separadas por vírgula"),
):
    """Compara preço de insumo ou composição entre estados."""
    return store.comparar(codigo=codigo, item=item, estados=estados)


@router.get("/previsao")
async def previsao(
    codigo: int = Query(..., description="Código do item"),
    item: str = Query("insumo", description="Tipo: insumo ou composicao"),
    estado: Optional[str] = Query(None),
    regime: Optional[str] = Query(None),
):
    """Previsão de preço de insumo ou composição."""
    return store.previsao(codigo=codigo, item=item, estado=estado, regime=regime)


# ---- Encargos --------------------------------------------------------------

@router.get("/encargos")
async def encargos(
    estado: Optional[str] = Query(None),
    regime: Optional[str] = Query("NAO_DESONERADO"),
):
    """Busca encargos sociais."""
    return store.buscar_encargos(estado=estado, regime=regime)


# ---- Indicadores -----------------------------------------------------------

@router.get("/indicadores")
async def indicadores(request: Request):
    """Lista indicadores econômicos."""
    params = dict(request.query_params)
    return store.listar_indicadores(**params)


# ---- Estados ---------------------------------------------------------------

@router.get("/estados")
async def estados(request: Request):
    """Lista estados disponíveis."""
    params = dict(request.query_params)
    return JSONResponse(content=store.listar_estados(**params))


# ---- Orçamento -------------------------------------------------------------

@router.get("/orcamento")
async def orcamento(
    itens: str = Query(..., description="Itens no formato [C|I]:codigo@quantidade,..."),
    estado: str = Query(..., description="UF"),
    regime: str = Query("NAO_DESONERADO"),
    bdi: Optional[float] = Query(None, description="Percentual BDI"),
):
    """Gera orçamento com base em itens e quantidades."""
    return store.gerar_orcamento(itens=itens, estado=estado, regime=regime, bdi=bdi)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _diagnose_zip(contents: bytes, filename: str) -> str:
    """Retorna informações diagnósticas sobre um ZIP SINAPI."""
    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as zf:
            names = zf.namelist()
            xlsx_files = [n for n in names if n.lower().endswith(".xlsx")]
            total = len(names)
            xlsx_count = len(xlsx_files)
            sample = xlsx_files[:5] if xlsx_files else names[:5]
            return (
                f"ZIP contém {total} itens, {xlsx_count} XLSX. "
                f"Exemplos: {sample}"
            )
    except Exception:
        return "Não foi possível analisar o ZIP."
