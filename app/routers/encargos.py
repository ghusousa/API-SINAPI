from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.services.data import ENCARGOS

router = APIRouter(prefix="/encargos", tags=["Encargos"])


@router.get("/buscar", summary="Buscar encargos sociais")
def buscar_encargos(
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """
    Retorna os percentuais de encargos sociais (horista e mensalista)
    para o estado informado.
    """
    estado = estado.lower()
    dados = ENCARGOS.get(estado)

    if dados is None:
        raise HTTPException(
            status_code=404,
            detail=f"Encargos não encontrados para o estado '{estado}'",
        )

    return dados
