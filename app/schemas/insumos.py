from pydantic import BaseModel, Field
from typing import Optional, List


class InsumoBusca(BaseModel):
    """Parâmetros para busca de insumos."""
    nome: Optional[str] = Field(None, description="Nome do insumo")
    codigo: Optional[int] = Field(None, description="Código SINAPI do insumo")
    estado: Optional[str] = Field(None, description="Sigla do estado (ex: sp)")
    referencia: Optional[str] = Field(None, description="Data de referência (YYYY-MM-DD)")
    modo_busca: Optional[str] = Field(None, description="Modo de busca")
    tipo: Optional[str] = Field(None, description="Tipo do insumo")
    familia: Optional[str] = Field(None, description="Família do insumo")
    regime: Optional[str] = Field(None, description="Regime: DESONERADO ou NAO_DESONERADO")
    sort: Optional[str] = Field(None, description="Campo para ordenação")
    order: Optional[str] = Field(None, description="Direção da ordenação (asc/desc)")
    data_ref: Optional[str] = Field(None, description="Data de referência alternativa")
    detail: Optional[bool] = Field(None, description="Incluir detalhes")
    page: Optional[int] = Field(1, ge=1, description="Página da paginação")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Limite de resultados por página")


class InsumoItem(BaseModel):
    """Representação de um insumo SINAPI."""
    codigo: int = Field(..., description="Código SINAPI do insumo")
    nome: str = Field(..., description="Nome/descrição do insumo")
    unidade: str = Field(..., description="Unidade de medida")
    preco: float = Field(..., description="Preço unitário")
    estado: str = Field(..., description="Sigla do estado")
    referencia: Optional[str] = Field(None, description="Data de referência")


class InsumoHistorico(BaseModel):
    """Parâmetros para consulta de histórico de preços de insumo."""
    codigo: int = Field(..., description="Código SINAPI do insumo")
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    periodo: Optional[str] = Field(None, description="Período (ex: 12m, 24m)")
    output: Optional[str] = Field(None, description="Formato de saída")


class InsumoComparar(BaseModel):
    """Parâmetros para comparação de insumo entre estados."""
    codigo: int = Field(..., description="Código SINAPI do insumo")
    estados: str = Field(..., description="Lista de estados separados por vírgula (ex: sp,rj,pb)")
    data_ref: Optional[str] = Field(None, description="Data de referência")
    output: Optional[str] = Field(None, description="Formato de saída")


class InsumoPrevisao(BaseModel):
    """Parâmetros para previsão de preço de insumo."""
    codigo: int = Field(..., description="Código SINAPI do insumo")
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    regime: Optional[str] = Field(None, description="Regime: DESONERADO ou NAO_DESONERADO")
    output: Optional[str] = Field(None, description="Formato de saída")
