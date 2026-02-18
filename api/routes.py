"""Rotas da API SINAPI.

Cada endpoint aceita os mesmos query-params da API oficial do Orçamentador
e serve os dados a partir dos arquivos SINAPI carregados localmente.
"""

import io
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile

from api.deps import verify_api_key
from api.data_store import store
from api.data_loader import load_zip_file, load_xlsx_file

router = APIRouter()


# ---- Upload de dados -------------------------------------------------------

@router.post("/upload", tags=["Admin"])
async def upload_sinapi(
    file: UploadFile = File(...),
    estado: Optional[str] = Query(None, description="UF do estado (obrigatório para XLSX avulso)"),
    referencia: Optional[str] = Query(None, description="Referência YYYY-MM (obrigatório para XLSX avulso)"),
):
    """Carrega um arquivo SINAPI (ZIP ou XLSX) no servidor."""
    contents = await file.read()
    filename = file.filename or ""

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

    store.load(data)

    return {
        "mensagem": "Dados carregados com sucesso",
        "insumos": len(data.get("insumos", [])),
        "composicoes": len(data.get("composicoes", [])),
        "analitico": len(data.get("analitico", [])),
    }


# ---- Insumos ---------------------------------------------------------------

@router.get("/insumos", dependencies=[Depends(verify_api_key)])
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

@router.get("/composicoes", dependencies=[Depends(verify_api_key)])
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


@router.get("/composicao", dependencies=[Depends(verify_api_key)])
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


@router.get("/composicao_explode", dependencies=[Depends(verify_api_key)])
async def explode_composicao(
    codigo: int = Query(..., description="Código da composição"),
    estado: Optional[str] = Query(None),
    regime: Optional[str] = Query(None),
):
    """Lista todos os insumos de uma composição (explodir)."""
    return store.explode_composicao(codigo=codigo, estado=estado, regime=regime)


# ---- Histórico / Comparar / Previsão (insumos e composições) ---------------

@router.get("/historico", dependencies=[Depends(verify_api_key)])
async def historico(
    codigo: int = Query(..., description="Código do item"),
    item: str = Query("insumo", description="Tipo: insumo ou composicao"),
    estado: Optional[str] = Query(None),
):
    """Histórico de preços de insumo ou composição."""
    return store.historico(codigo=codigo, item=item, estado=estado)


@router.get("/comparar", dependencies=[Depends(verify_api_key)])
async def comparar(
    codigo: int = Query(..., description="Código do item"),
    item: str = Query("insumo", description="Tipo: insumo ou composicao"),
    estados: Optional[str] = Query(None, description="UFs separadas por vírgula"),
):
    """Compara preço de insumo ou composição entre estados."""
    return store.comparar(codigo=codigo, item=item, estados=estados)


@router.get("/previsao", dependencies=[Depends(verify_api_key)])
async def previsao(
    codigo: int = Query(..., description="Código do item"),
    item: str = Query("insumo", description="Tipo: insumo ou composicao"),
    estado: Optional[str] = Query(None),
    regime: Optional[str] = Query(None),
):
    """Previsão de preço de insumo ou composição."""
    return store.previsao(codigo=codigo, item=item, estado=estado, regime=regime)


# ---- Encargos --------------------------------------------------------------

@router.get("/encargos", dependencies=[Depends(verify_api_key)])
async def encargos(request: Request):
    """Busca encargos sociais."""
    params = dict(request.query_params)
    return store.buscar_encargos(**params)


# ---- Indicadores -----------------------------------------------------------

@router.get("/indicadores", dependencies=[Depends(verify_api_key)])
async def indicadores(request: Request):
    """Lista indicadores econômicos."""
    params = dict(request.query_params)
    return store.listar_indicadores(**params)


# ---- Estados ---------------------------------------------------------------

@router.get("/estados", dependencies=[Depends(verify_api_key)])
async def estados(request: Request):
    """Lista estados disponíveis."""
    params = dict(request.query_params)
    if "ibge" in params:
        params["ibge"] = int(params["ibge"])
    return store.listar_estados(**params)


# ---- Orçamento -------------------------------------------------------------

@router.get("/orcamento", dependencies=[Depends(verify_api_key)])
async def orcamento(
    itens: str = Query(..., description="Itens no formato [C|I]:codigo@quantidade,..."),
    estado: str = Query(..., description="UF"),
    regime: str = Query("NAO_DESONERADO"),
    bdi: Optional[float] = Query(None, description="Percentual BDI"),
):
    """Gera orçamento com base em itens e quantidades."""
    return store.gerar_orcamento(itens=itens, estado=estado, regime=regime, bdi=bdi)
