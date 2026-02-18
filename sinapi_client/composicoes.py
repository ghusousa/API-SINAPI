"""Recurso de Composições da API SINAPI."""


class Composicoes:
    """Consulta de composições da tabela SINAPI."""

    def __init__(self, http):
        self._http = http

    def buscar(self, **params):
        """Busca composições por nome, código ou filtros.

        Args:
            nome: Nome da composição.
            codigo: Código da composição.
            estado: UF (ex: 'sp').
            referencia: Data de referência (ex: '2025-09-01').
            page: Página para paginação.
            limit: Limite de resultados.
            modo_busca: Modo de busca.
            filtro: Filtro.
            regime: Regime (DESONERADO/NAO_DESONERADO).
            sort: Campo de ordenação.
            order: Direção da ordenação.
            output: Formato de saída.
            data_ref: Data de referência alternativa.

        Returns:
            dict: Dados das composições encontradas.
        """
        return self._http.get("/composicoes", params=params)

    def detalhar(self, **params):
        """Detalha uma composição específica.

        Args:
            codigo: Código da composição (obrigatório).
            estado: UF (ex: 'sp').
            regime: Regime (DESONERADO/NAO_DESONERADO).
            output: Formato de saída.
            data_ref: Data de referência.

        Returns:
            dict: Detalhes da composição.
        """
        return self._http.get("/composicao", params=params)

    def explode(self, **params):
        """Lista todos os insumos de uma composição (explodir composição).

        Args:
            codigo: Código da composição (obrigatório).
            estado: UF (ex: 'sp').
            regime: DESONERADO ou NAO_DESONERADO.
            output: Formato de saída.
            data_ref: Data de referência.
            sort: Campo de ordenação.
            order: Direção da ordenação.

        Returns:
            dict: Insumos que compõem a composição.
        """
        return self._http.get("/composicao_explode", params=params)

    def historico(self, **params):
        """Busca histórico de custos de uma composição.

        Args:
            codigo: Código da composição (obrigatório).
            estado: UF (ex: 'sp').
            periodo: Período do histórico.
            output: Formato de saída.

        Returns:
            dict: Histórico de custos da composição.
        """
        params["item"] = "composicao"
        return self._http.get("/historico", params=params)

    def comparar(self, **params):
        """Compara o custo de uma composição entre estados.

        Args:
            codigo: Código da composição (obrigatório).
            estados: UFs separadas por vírgula (ex: 'sp,rj,pb').
            data_ref: Data de referência.
            output: Formato de saída.

        Returns:
            dict: Comparação de custos entre estados.
        """
        params["item"] = "composicao"
        return self._http.get("/comparar", params=params)

    def previsao(self, **params):
        """Previsão de custo de uma composição.

        Args:
            codigo: Código da composição (obrigatório).
            estado: UF (ex: 'sp').
            regime: DESONERADO ou NAO_DESONERADO.
            output: Formato de saída.

        Returns:
            dict: Previsão de custo da composição.
        """
        params["item"] = "composicao"
        return self._http.get("/previsao", params=params)
