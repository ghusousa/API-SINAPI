from pydantic import BaseModel, Field
from typing import Optional


class OrcamentoGerar(BaseModel):
    """Parâmetros para geração de orçamento."""
    itens: str = Field(
        ...,
        description=(
            "Itens do orçamento no formato [C|I]:codigo@quantidade separados por vírgula. "
            "C = composição, I = insumo. Ex: C:12321@3.2,I:234@12.5,I:3773@7"
        ),
    )
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    regime: Optional[str] = Field(None, description="Regime: DESONERADO ou NAO_DESONERADO")
    bdi: Optional[float] = Field(None, description="Percentual de BDI a aplicar")
    data_ref: Optional[str] = Field(None, description="Data de referência")
    output: Optional[str] = Field(None, description="Formato de saída")


class OrcamentoItemResult(BaseModel):
    """Item individual do orçamento gerado."""
    tipo: str = Field(..., description="Tipo do item (insumo ou composicao)")
    codigo: int = Field(..., description="Código SINAPI")
    nome: str = Field(..., description="Descrição do item")
    unidade: str = Field(..., description="Unidade de medida")
    preco_unitario: float = Field(..., description="Preço unitário")
    quantidade: float = Field(..., description="Quantidade")
    preco_total: float = Field(..., description="Preço total (unitário × quantidade)")
