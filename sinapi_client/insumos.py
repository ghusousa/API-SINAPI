"""Recurso de Insumos da API SINAPI."""


class Insumos:
    """Consulta de insumos da tabela SINAPI."""

    def __init__(self, http):
        self._http = http

    def buscar(self, **params):
        """Busca insumos por nome, código ou filtros.

        Args:
            nome: Nome do insumo.
            codigo: Código do insumo.
            estado: UF (ex: 'sp').
            referencia: Data de referência (ex: '2025-09-01').
            page: Página para paginação.
            limit: Limite de resultados.
            modo_busca: Modo de busca.
            tipo: Tipo do insumo.
            familia: Família do insumo.
            regime: Regime (DESONERADO/NAO_DESONERADO).
            sort: Campo de ordenação.
            order: Direção da ordenação.
            output: Formato de saída.
            data_ref: Data de referência alternativa.
            detail: Nível de detalhe.

        Returns:
            dict: Dados dos insumos encontrados.
        """
        return self._http.get("/insumos", params=params)

    def historico(self, **params):
        """Busca histórico de preços de um insumo.

        Args:
            codigo: Código do insumo (obrigatório).
            estado: UF (ex: 'sp').
            periodo: Período do histórico.
            output: Formato de saída.

        Returns:
            dict: Histórico de preços do insumo.
        """
        params["item"] = "insumo"
        return self._http.get("/historico", params=params)

    def comparar(self, **params):
        """Compara o preço de um insumo entre estados.

        Args:
            codigo: Código do insumo (obrigatório).
            estados: UFs separadas por vírgula (ex: 'sp,rj,pb').
            data_ref: Data de referência.
            output: Formato de saída.

        Returns:
            dict: Comparação de preços entre estados.
        """
        params["item"] = "insumo"
        return self._http.get("/comparar", params=params)

    def previsao(self, **params):
        """Previsão de preço de um insumo.

        Args:
            codigo: Código do insumo (obrigatório).
            estado: UF (ex: 'sp').
            regime: DESONERADO ou NAO_DESONERADO.
            output: Formato de saída.

        Returns:
            dict: Previsão de preço do insumo.
        """
        params["item"] = "insumo"
        return self._http.get("/previsao", params=params)
