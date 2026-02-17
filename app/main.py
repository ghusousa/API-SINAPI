from fastapi import FastAPI

from app.routers import insumos, composicoes, orcamento, estados, indicadores, encargos

app = FastAPI(
    title="API SINAPI - Sistema de Orçamento",
    description=(
        "API para consulta de insumos e composições da tabela SINAPI, "
        "geração de orçamentos, indicadores econômicos, estados e encargos sociais."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.include_router(insumos.router)
app.include_router(composicoes.router)
app.include_router(orcamento.router)
app.include_router(estados.router)
app.include_router(indicadores.router)
app.include_router(encargos.router)


@app.get("/", tags=["Root"])
def root():
    """Health-check / informações básicas da API."""
    return {
        "api": "API SINAPI",
        "versao": "1.0.0",
        "documentacao": "/api/docs",
    }
