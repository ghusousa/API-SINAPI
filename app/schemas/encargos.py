from pydantic import BaseModel, Field
from typing import Optional


class EncargosBusca(BaseModel):
    """Parâmetros para busca de encargos sociais."""
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    output: Optional[str] = Field(None, description="Formato de saída")


class EncargosItem(BaseModel):
    """Representação de encargos sociais."""
    estado: str = Field(..., description="Sigla do estado")
    horista: Optional[float] = Field(None, description="Percentual de encargos para horista")
    mensalista: Optional[float] = Field(None, description="Percentual de encargos para mensalista")
    referencia: Optional[str] = Field(None, description="Data de referência")
