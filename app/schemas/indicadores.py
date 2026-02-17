from pydantic import BaseModel, Field
from typing import Optional


class IndicadorListar(BaseModel):
    """Parâmetros para listagem de indicadores econômicos."""
    indicadores: Optional[str] = Field(
        None,
        description=(
            "Lista de indicadores separados por vírgula. "
            "Opções: incc, incc_acumulado, ipca, igpm, selic, dolar"
        ),
    )
    output: Optional[str] = Field(None, description="Formato de saída")


class IndicadorItem(BaseModel):
    """Representação de um indicador econômico."""
    nome: str = Field(..., description="Nome do indicador")
    valor: float = Field(..., description="Valor atual do indicador")
    referencia: str = Field(..., description="Data de referência")
