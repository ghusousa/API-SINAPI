"""Recurso de Encargos da API SINAPI."""


class Encargos:
    """Consulta de encargos sociais da tabela SINAPI."""

    def __init__(self, http):
        self._http = http

    def buscar(self, **params):
        """Busca encargos sociais.

        Args:
            estado: UF (ex: 'sp').
            output: Formato de saída.

        Returns:
            dict: Encargos sociais.
        """
        return self._http.get("/encargos", params=params or None)
