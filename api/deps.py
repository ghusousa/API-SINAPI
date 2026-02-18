"""Dependências de autenticação e configuração da API."""

import os
from typing import Optional

from fastapi import Header, HTTPException


API_KEYS: set[str] = set()

_env_keys = os.environ.get("API_KEYS", "")
if _env_keys:
    API_KEYS.update(k.strip() for k in _env_keys.split(",") if k.strip())


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Valida a chave de API enviada no header ``X-API-Key``.

    Raises:
        HTTPException 401: Se a chave não for informada ou for inválida.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header ausente")
    if API_KEYS and x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Chave de API inválida")
    return x_api_key
