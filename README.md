# API-SINAPI

API e cliente Python para a **API SINAPI do Orçamentador** ([www.orcamentador.com.br/api/docs](https://www.orcamentador.com.br/api/docs)).

Este projeto contém:

1. **Servidor API** (`api/`) — API FastAPI que replica todos os endpoints da API oficial do Orçamentador, fazendo proxy das requisições.
2. **Cliente Python** (`sinapi_client/`) — Biblioteca para consumo da API.

---

## Instalação

```bash
pip install -e .
```

Requisitos: Python >= 3.8, [requests](https://pypi.org/project/requests/), [FastAPI](https://fastapi.tiangolo.com/), [uvicorn](https://www.uvicorn.org/), [httpx](https://www.python-httpx.org/).

---

## Servidor API

O servidor replica todos os endpoints da API oficial do Orçamentador, protegidos por autenticação via `X-API-Key`.

### Configuração

Defina as variáveis de ambiente:

```bash
# Chave(s) de API aceitas pelo nosso servidor (separadas por vírgula)
export API_KEYS="chave1,chave2"

# Chave de API para acessar a API upstream do Orçamentador
export UPSTREAM_API_KEY="SUA_CHAVE_ORCAMENTADOR"
```

### Iniciar o servidor

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### Documentação interativa

Acesse `http://localhost:8000/docs` para a interface Swagger UI.

### Endpoints disponíveis

| Endpoint              | Descrição                                      |
|-----------------------|------------------------------------------------|
| `GET /insumos`        | Busca insumos por nome, código ou filtros       |
| `GET /composicoes`    | Busca composições por nome, código ou filtros   |
| `GET /composicao`     | Detalha uma composição específica               |
| `GET /composicao_explode` | Lista todos os insumos de uma composição    |
| `GET /historico`      | Histórico de preços (insumo ou composição)      |
| `GET /comparar`       | Compara preço entre estados                     |
| `GET /previsao`       | Previsão de preço                               |
| `GET /encargos`       | Encargos sociais                                |
| `GET /indicadores`    | Indicadores econômicos                          |
| `GET /estados`        | Lista estados disponíveis                       |
| `GET /orcamento`      | Gera orçamento com base em itens e quantidades  |

### Exemplo de chamada

```bash
curl -H "X-API-Key: SUA_CHAVE" "http://localhost:8000/insumos?nome=cimento&estado=sp&limit=10"
```

---

## Cliente Python

## Autenticação

A autenticação é feita via chave de API, enviada no header `X-API-Key`.

Você pode informar a chave diretamente ou pela variável de ambiente `ORCAMENTADOR_API_KEY`:

```bash
export ORCAMENTADOR_API_KEY="SUA_API_KEY"
```

```python
from sinapi_client import Client

# Via parâmetro
client = Client(api_key="SUA_API_KEY")

# Ou via variável de ambiente
client = Client()
```

---

## Uso

### Insumos

```python
# Buscar insumos
client.insumos.buscar(nome="cimento", estado="sp", limit=10)

# Histórico de preço
client.insumos.historico(codigo=123, estado="sp")

# Comparar entre estados
client.insumos.comparar(codigo=123, estados="sp,rj,pb")

# Previsão de preço
client.insumos.previsao(codigo=123, estado="sp", regime="DESONERADO")
```

### Composições

```python
# Buscar composições
client.composicoes.buscar(nome="argamassa", estado="sp", limit=50)

# Detalhar composição
client.composicoes.detalhar(codigo=123456, estado="sp")

# Explodir composição (listar insumos)
client.composicoes.explode(codigo=123456, estado="sp", regime="DESONERADO")

# Histórico de custo
client.composicoes.historico(codigo=123456, estado="sp")

# Comparar entre estados
client.composicoes.comparar(codigo=123456, estados="sp,rj,pb")

# Previsão de custo
client.composicoes.previsao(codigo=123456, estado="sp", regime="NAO_DESONERADO")
```

### Encargos

```python
client.encargos.buscar(estado="sp")
```

### Indicadores

```python
client.indicadores.listar(indicadores="incc,incc_acumulado,ipca,igpm,selic,dolar")
```

### Estados

```python
# Listar todos
client.estados.listar()

# Filtrar
client.estados.listar(estado="sp")
client.estados.listar(ibge=35)
client.estados.listar(regiao="sudeste")
```

### Orçamento

```python
client.orcamento.gerar(
    itens="C:12321@3.2,I:234@12.5,I:3773@7",
    estado="sp",
    regime="DESONERADO",
)
```

---

## Tratamento de erros

```python
from sinapi_client import Client, AuthenticationException, ApiException

client = Client(api_key="SUA_API_KEY")

try:
    resultado = client.insumos.buscar(nome="cimento")
except AuthenticationException as e:
    print(f"Erro de autenticação: {e}")
except ApiException as e:
    print(f"Erro da API: {e}")
```

Exceções disponíveis: `ApiException`, `AuthenticationException`, `NotFoundException`, `RateLimitException`, `ServerException`.

---

## Testes

```bash
pip install pytest
pytest
```

---

## Links

- 🌐 Site: https://www.orcamentador.com.br
- 📘 Documentação da API: https://www.orcamentador.com.br/api/docs
- 🐙 SDK oficial (PHP): https://github.com/orcamentador/orcamentador-sdk