"""Aplicação FastAPI – API SINAPI.

Replica os mesmos endpoints da API oficial do Orçamentador
(https://www.orcamentador.com.br/api/docs), fazendo proxy das
requisições e entregando os resultados no mesmo formato.
"""

from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="API SINAPI",
    description=(
        "API que replica os endpoints da API SINAPI do Orçamentador "
        "(www.orcamentador.com.br/api/docs). Autenticação via header X-API-Key."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)
