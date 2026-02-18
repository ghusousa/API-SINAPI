"""Recurso de Orçamento da API SINAPI."""


class Orcamento:
    """Geração de orçamentos com base na tabela SINAPI."""

    def __init__(self, http):
        self._http = http

    def gerar(self, **params):
        """Gera um orçamento com base em itens e quantidades.

        Args:
            itens: Itens no formato '[C|I]:codigo@quantidade,...'
                   (ex: 'C:12321@3.2,I:234@12.5,I:3773@7').
            estado: UF (ex: 'sp').
            regime: DESONERADO ou NAO_DESONERADO.
            bdi: Percentual de BDI.
            output: Formato de saída.
            data_ref: Data de referência.

        Returns:
            dict: Orçamento gerado.
        """
        return self._http.get("/orcamento", params=params)
