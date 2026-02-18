"""Recurso de Estados da API SINAPI."""


class Estados:
    """Consulta de estados disponíveis na tabela SINAPI."""

    def __init__(self, http):
        self._http = http

    def listar(self, **params):
        """Lista estados disponíveis.

        Args:
            estado: UF (ex: 'sp').
            ibge: Código IBGE (ex: 35).
            regiao: Região (ex: 'sudeste').
            output: Formato de saída.

        Returns:
            dict: Estados disponíveis.
        """
        return self._http.get("/estados", params=params or None)
