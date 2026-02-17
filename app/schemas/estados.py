from pydantic import BaseModel, Field
from typing import Optional


class EstadoListar(BaseModel):
    """Parâmetros para listagem de estados."""
    estado: Optional[str] = Field(None, description="Sigla do estado (ex: sp)")
    ibge: Optional[int] = Field(None, description="Código IBGE do estado")
    regiao: Optional[str] = Field(None, description="Região geográfica (ex: sudeste)")
    output: Optional[str] = Field(None, description="Formato de saída")


class EstadoItem(BaseModel):
    """Representação de um estado."""
    nome: str = Field(..., description="Nome do estado")
    sigla: str = Field(..., description="Sigla do estado")
    ibge: int = Field(..., description="Código IBGE")
    regiao: str = Field(..., description="Região geográfica")
