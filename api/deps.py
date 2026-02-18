"""Dependências de autenticação e configuração da API."""

import os
from typing import Optional

from fastapi import Header, HTTPException


def _load_api_keys() -> frozenset[str]:
    """Carrega chaves da variável de ambiente ``API_KEYS``."""
    env = os.environ.get("API_KEYS", "")
    return frozenset(k.strip() for k in env.split(",") if k.strip())


API_KEYS: frozenset[str] = _load_api_keys()


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Valida a chave de API enviada no header ``X-API-Key``.

    Quando nenhuma chave está configurada em ``API_KEYS``, qualquer chave
    presente no header é aceita (modo desenvolvimento).

    Raises:
        HTTPException 401: Se a chave não for informada ou for inválida.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header ausente")
    if API_KEYS and x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    return x_api_key
