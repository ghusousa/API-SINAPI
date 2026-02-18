"""Cliente principal para a API SINAPI do Orçamentador."""

import os

from sinapi_client.http_client import HttpClient
from sinapi_client.insumos import Insumos
from sinapi_client.composicoes import Composicoes
from sinapi_client.encargos import Encargos
from sinapi_client.indicadores import Indicadores
from sinapi_client.estados import Estados
from sinapi_client.orcamento import Orcamento

BASE_URL = "https://orcamentador.com.br/api"


class Client:
    """Cliente para consumo da API SINAPI do Orçamentador.

    A autenticação é feita via chave de API enviada no header ``X-API-Key``.

    Args:
        api_key: Chave de API. Se não informada, será lida da variável de
            ambiente ``ORCAMENTADOR_API_KEY``.
        base_url: URL base da API (padrão: ``https://orcamentador.com.br/api``).
        timeout: Tempo limite para requisições em segundos (padrão: 20).

    Raises:
        ValueError: Se nenhuma chave de API for fornecida.

    Exemplo::

        from sinapi_client import Client

        client = Client(api_key="SUA_API_KEY")
        resultado = client.insumos.buscar(nome="cimento", estado="sp")
    """

    def __init__(self, api_key=None, base_url=BASE_URL, timeout=20):
        if api_key is None:
            api_key = os.environ.get("ORCAMENTADOR_API_KEY")
        if not api_key:
            raise ValueError(
                "É necessário fornecer uma chave de API via parâmetro 'api_key' "
                "ou pela variável de ambiente 'ORCAMENTADOR_API_KEY'."
            )

        self._http = HttpClient(base_url, api_key, timeout)

        self.insumos = Insumos(self._http)
        self.composicoes = Composicoes(self._http)
        self.encargos = Encargos(self._http)
        self.indicadores = Indicadores(self._http)
        self.estados = Estados(self._http)
        self.orcamento = Orcamento(self._http)
