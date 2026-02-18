"""Rotas da API SINAPI.

Cada endpoint aceita os mesmos query-params da API oficial do Orçamentador
e faz proxy da requisição, devolvendo os dados no mesmo formato.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from api.deps import verify_api_key
from api.proxy import proxy_request

router = APIRouter(dependencies=[Depends(verify_api_key)])


# ---- Insumos ---------------------------------------------------------------

@router.get("/insumos")
async def buscar_insumos(request: Request):
    """Busca insumos por nome, código ou filtros."""
    return await proxy_request("/insumos", request.query_params)


# ---- Composições -----------------------------------------------------------

@router.get("/composicoes")
async def buscar_composicoes(request: Request):
    """Busca composições por nome, código ou filtros."""
    return await proxy_request("/composicoes", request.query_params)


@router.get("/composicao")
async def detalhar_composicao(request: Request):
    """Detalha uma composição específica."""
    return await proxy_request("/composicao", request.query_params)


@router.get("/composicao_explode")
async def explode_composicao(request: Request):
    """Lista todos os insumos de uma composição (explodir)."""
    return await proxy_request("/composicao_explode", request.query_params)


# ---- Histórico / Comparar / Previsão (insumos e composições) ---------------

@router.get("/historico")
async def historico(request: Request):
    """Histórico de preços de insumo ou composição."""
    return await proxy_request("/historico", request.query_params)


@router.get("/comparar")
async def comparar(request: Request):
    """Compara preço de insumo ou composição entre estados."""
    return await proxy_request("/comparar", request.query_params)


@router.get("/previsao")
async def previsao(request: Request):
    """Previsão de preço de insumo ou composição."""
    return await proxy_request("/previsao", request.query_params)


# ---- Encargos --------------------------------------------------------------

@router.get("/encargos")
async def encargos(request: Request):
    """Busca encargos sociais."""
    return await proxy_request("/encargos", request.query_params)


# ---- Indicadores -----------------------------------------------------------

@router.get("/indicadores")
async def indicadores(request: Request):
    """Lista indicadores econômicos."""
    return await proxy_request("/indicadores", request.query_params)


# ---- Estados ---------------------------------------------------------------

@router.get("/estados")
async def estados(request: Request):
    """Lista estados disponíveis."""
    return await proxy_request("/estados", request.query_params)


# ---- Orçamento -------------------------------------------------------------

@router.get("/orcamento")
async def orcamento(request: Request):
    """Gera orçamento com base em itens e quantidades."""
    return await proxy_request("/orcamento", request.query_params)
