from fastapi import APIRouter, Query
from typing import Optional

from app.services.data import ESTADOS

router = APIRouter(prefix="/estados", tags=["Estados"])


@router.get("/listar", summary="Listar estados")
def listar_estados(
    estado: Optional[str] = Query(None, description="Sigla do estado (ex: sp)"),
    ibge: Optional[int] = Query(None, description="Código IBGE do estado"),
    regiao: Optional[str] = Query(None, description="Região geográfica (ex: sudeste)"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """
    Lista os estados disponíveis na base SINAPI.

    Permite filtrar por sigla, código IBGE ou região.
    Se nenhum filtro for informado, retorna todos os estados.
    """
    resultados = ESTADOS

    if estado is not None:
        resultados = [e for e in resultados if e["sigla"] == estado.lower()]

    if ibge is not None:
        resultados = [e for e in resultados if e["ibge"] == ibge]

    if regiao is not None:
        resultados = [e for e in resultados if e["regiao"] == regiao.lower()]

    return {"total": len(resultados), "estados": resultados}
