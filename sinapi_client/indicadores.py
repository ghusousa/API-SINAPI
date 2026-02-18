"""Recurso de Indicadores da API SINAPI."""


class Indicadores:
    """Consulta de indicadores econômicos."""

    def __init__(self, http):
        self._http = http

    def listar(self, **params):
        """Lista indicadores econômicos.

        Args:
            indicadores: Lista de indicadores separados por vírgula
                         (ex: 'incc,incc_acumulado,ipca,igpm,selic,dolar').
            output: Formato de saída.

        Returns:
            dict: Indicadores econômicos.
        """
        return self._http.get("/indicadores", params=params)
