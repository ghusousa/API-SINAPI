from fastapi import APIRouter, Query
from typing import Optional

from app.services.data import INDICADORES

router = APIRouter(prefix="/indicadores", tags=["Indicadores"])


@router.get("/listar", summary="Listar indicadores econômicos")
def listar_indicadores(
    indicadores: Optional[str] = Query(
        None,
        description=(
            "Lista de indicadores separados por vírgula. "
            "Opções: incc, incc_acumulado, ipca, igpm, selic, dolar"
        ),
    ),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """
    Lista indicadores econômicos relevantes para o setor da construção civil.

    Se nenhum indicador for informado, retorna todos os disponíveis.
    """
    resultados = INDICADORES

    if indicadores is not None:
        lista = [i.strip().lower() for i in indicadores.split(",")]
        resultados = [ind for ind in resultados if ind["nome"] in lista]

    return {"total": len(resultados), "indicadores": resultados}
