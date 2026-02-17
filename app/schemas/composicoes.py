from pydantic import BaseModel, Field
from typing import Optional, List


class ComposicaoBusca(BaseModel):
    """Parâmetros para busca de composições."""
    nome: Optional[str] = Field(None, description="Nome da composição")
    codigo: Optional[int] = Field(None, description="Código SINAPI da composição")
    estado: Optional[str] = Field(None, description="Sigla do estado (ex: sp)")
    referencia: Optional[str] = Field(None, description="Data de referência (YYYY-MM-DD)")
    modo_busca: Optional[str] = Field(None, description="Modo de busca")
    filtro: Optional[str] = Field(None, description="Filtro adicional")
    regime: Optional[str] = Field(None, description="Regime: DESONERADO ou NAO_DESONERADO")
    sort: Optional[str] = Field(None, description="Campo para ordenação")
    order: Optional[str] = Field(None, description="Direção da ordenação (asc/desc)")
    data_ref: Optional[str] = Field(None, description="Data de referência alternativa")
    page: Optional[int] = Field(1, ge=1, description="Página da paginação")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Limite de resultados por página")


class ComposicaoItem(BaseModel):
    """Representação de uma composição SINAPI."""
    codigo: int = Field(..., description="Código SINAPI da composição")
    nome: str = Field(..., description="Nome/descrição da composição")
    unidade: str = Field(..., description="Unidade de medida")
    preco: float = Field(..., description="Preço total da composição")
    estado: str = Field(..., description="Sigla do estado")
    referencia: Optional[str] = Field(None, description="Data de referência")


class ComposicaoDetalhar(BaseModel):
    """Parâmetros para detalhamento de composição."""
    codigo: int = Field(..., description="Código SINAPI da composição")
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    regime: Optional[str] = Field(None, description="Regime: DESONERADO ou NAO_DESONERADO")
    data_ref: Optional[str] = Field(None, description="Data de referência")
    output: Optional[str] = Field(None, description="Formato de saída")


class ComposicaoExplode(BaseModel):
    """Parâmetros para explosão de composição."""
    codigo: int = Field(..., description="Código SINAPI da composição")
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    regime: Optional[str] = Field(None, description="Regime: DESONERADO ou NAO_DESONERADO")
    data_ref: Optional[str] = Field(None, description="Data de referência")
    sort: Optional[str] = Field(None, description="Campo para ordenação")
    order: Optional[str] = Field(None, description="Direção da ordenação (asc/desc)")
    output: Optional[str] = Field(None, description="Formato de saída")


class ComposicaoHistorico(BaseModel):
    """Parâmetros para consulta de histórico de composição."""
    codigo: int = Field(..., description="Código SINAPI da composição")
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    periodo: Optional[str] = Field(None, description="Período (ex: 12m, 24m)")
    output: Optional[str] = Field(None, description="Formato de saída")


class ComposicaoComparar(BaseModel):
    """Parâmetros para comparação de composição entre estados."""
    codigo: int = Field(..., description="Código SINAPI da composição")
    estados: str = Field(..., description="Lista de estados separados por vírgula (ex: sp,rj,pb)")
    data_ref: Optional[str] = Field(None, description="Data de referência")
    output: Optional[str] = Field(None, description="Formato de saída")


class ComposicaoPrevisao(BaseModel):
    """Parâmetros para previsão de preço de composição."""
    codigo: int = Field(..., description="Código SINAPI da composição")
    estado: str = Field(..., description="Sigla do estado (ex: sp)")
    regime: Optional[str] = Field(None, description="Regime: DESONERADO ou NAO_DESONERADO")
    output: Optional[str] = Field(None, description="Formato de saída")
