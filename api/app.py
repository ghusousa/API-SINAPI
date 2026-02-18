"""Aplicação FastAPI – API SINAPI.

Processa arquivos SINAPI XLSX/ZIP da Caixa Econômica Federal e serve
os dados através de endpoints compatíveis com a API do Orçamentador
(https://www.orcamentador.com.br/api/docs).
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Carrega dados SINAPI na inicialização se SINAPI_DATA_DIR estiver definido."""
    data_dir = os.environ.get("SINAPI_DATA_DIR", "")
    if data_dir and os.path.isdir(data_dir):
        from api.data_loader import load_zip_file, load_xlsx_file, _detect_estado_from_filename, _detect_referencia_from_filename
        from api.data_store import store

        for fname in sorted(os.listdir(data_dir)):
            fpath = os.path.join(data_dir, fname)
            if fname.lower().endswith(".zip"):
                data = load_zip_file(fpath)
                store.load(data)
            elif fname.lower().endswith(".xlsx"):
                estado = _detect_estado_from_filename(fname)
                ref = _detect_referencia_from_filename(fname)
                if estado and ref:
                    data = load_xlsx_file(fpath, estado, ref)
                    store.load(data)
    yield


app = FastAPI(
    title="API SINAPI",
    description=(
        "API que processa arquivos SINAPI (XLSX/ZIP) da Caixa Econômica Federal "
        "e serve os dados com endpoints compatíveis com a API do Orçamentador "
        "(www.orcamentador.com.br/api/docs)."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(router)
