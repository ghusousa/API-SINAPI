"""Exceções personalizadas para a API do Orçamentador."""


class ApiException(Exception):
    """Exceção base para erros da API."""

    def __init__(self, message="Erro na requisição", status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationException(ApiException):
    """Erro de autenticação (401/403)."""


class NotFoundException(ApiException):
    """Recurso não encontrado (404)."""


class RateLimitException(ApiException):
    """Limite de requisições excedido (429)."""


class ServerException(ApiException):
    """Erro interno do servidor (5xx)."""
