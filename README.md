# API-SINAPI

API e cliente Python para dados **SINAPI** (Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil).

Processa os arquivos XLSX/ZIP publicados mensalmente pela **Caixa Econômica Federal** e serve os dados através de endpoints compatíveis com a API do Orçamentador ([www.orcamentador.com.br/api/docs](https://www.orcamentador.com.br/api/docs)).

---

## Início Rápido (1 clique)

**Windows:** Dê duplo clique em `iniciar.bat`

**Linux/Mac:**
```bash
./iniciar.sh
```

O script irá automaticamente:
1. ✅ Verificar se o Python está instalado
2. ✅ Criar um ambiente virtual (`.venv`)
3. ✅ Instalar todas as dependências
4. ✅ Iniciar o servidor na porta 8000
5. ✅ Abrir o Swagger UI no navegador (`http://localhost:8000/docs`)

> **Requisito:** Python 3.8+ instalado. Baixe em https://www.python.org/downloads/ (marque "Add Python to PATH").

---

## Instalação manual

```bash
pip install -e .
```

Requisitos: Python >= 3.8

---

## Servidor API

### Iniciar

```bash
# Opcional: carregar dados automaticamente na inicialização
export SINAPI_DATA_DIR="/caminho/para/arquivos/sinapi"

uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### Carregar dados SINAPI

Faça upload do arquivo ZIP mensal da Caixa (ex: `SINAPI-2026-01-formato-xlsx.zip`):

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@SINAPI-2026-01-formato-xlsx.zip"
```

Ou de um XLSX avulso por estado:

```bash
curl -X POST "http://localhost:8000/upload?estado=SP&referencia=2026-01" \
  -F "file=@SINAPI_Preco_Ref_SP_202601.xlsx"
```

### Documentação interativa

Acesse `http://localhost:8000/docs` para a interface Swagger UI.

### Endpoints disponíveis

| Endpoint              | Descrição                                      |
|-----------------------|------------------------------------------------|
| `POST /upload`        | Carrega arquivo SINAPI (ZIP ou XLSX)            |
| `GET /insumos`        | Busca insumos por nome, código ou filtros       |
| `GET /composicoes`    | Busca composições por nome, código ou filtros   |
| `GET /composicao`     | Detalha uma composição com seus itens           |
| `GET /composicao_explode` | Lista todos os insumos de uma composição    |
| `GET /historico`      | Histórico de preços (insumo ou composição)      |
| `GET /comparar`       | Compara preço entre estados                     |
| `GET /previsao`       | Previsão de preço                               |
| `GET /encargos`       | Encargos sociais                                |
| `GET /indicadores`    | Indicadores econômicos                          |
| `GET /estados`        | Lista estados disponíveis                       |
| `GET /orcamento`      | Gera orçamento com base em itens e quantidades  |

### Exemplos de uso

```bash
# Buscar insumos
curl "http://localhost:8000/insumos?nome=cimento&estado=SP&limit=10"

# Detalhar composição
curl "http://localhost:8000/composicao?codigo=87316&estado=SP"

# Gerar orçamento
curl "http://localhost:8000/orcamento?itens=C:87316@2.0,I:370@100&estado=SP&regime=NAO_DESONERADO"
```

---

## Cliente Python

```python
from sinapi_client import Client

client = Client(base_url="http://localhost:8000")
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
from sinapi_client import Client, ApiException

client = Client(base_url="http://localhost:8000")

try:
    resultado = client.insumos.buscar(nome="cimento")
except ApiException as e:
    print(f"Erro da API: {e}")
```

Exceções disponíveis: `ApiException`, `NotFoundException`, `ServerException`.

---

## Como Testar

Há **3 formas** de testar a API:

### 1. Script de teste rápido (recomendado)

Executa o servidor com dados de amostra e testa **todos os 19 endpoints automaticamente**:

```bash
python scripts/testar_api.py
```

Saída esperada:
```
🚀 Iniciando servidor API SINAPI na porta 8777...
✓ Servidor pronto!

  1. Upload de Dados SINAPI
  ✓ Upload XLSX com dados de amostra: OK

  2. Insumos (/insumos)
  ✓ Buscar por nome: OK
  ✓ Buscar por código: OK
  ...

  ✓ TODOS OS 17 TESTES PASSARAM!
```

### 2. Testes unitários (pytest)

```bash
pip install pytest anyio pytest-anyio
pytest -v
```

Cobertura:
- `tests/test_api.py` — 24 testes dos endpoints da API
- `tests/test_client.py` — 27 testes do cliente Python
- `tests/test_data_loader.py` — 27 testes do parser XLSX/ZIP

### 3. Teste manual (Swagger UI + curl)

Inicie o servidor e use a interface interativa:

```bash
# Iniciar o servidor
uvicorn api.app:app --port 8000

# Abra no navegador:
# http://localhost:8000/docs
```

Ou teste via curl:

```bash
# 1. Carregar dados de amostra (gera um XLSX de teste)
python -c "
from tests.sample_data import create_sample_sinapi_xlsx
xlsx = create_sample_sinapi_xlsx('SP', '2026-01')
with open('/tmp/sinapi_sp.xlsx', 'wb') as f:
    f.write(xlsx.getvalue())
print('Arquivo criado: /tmp/sinapi_sp.xlsx')
"

# 2. Fazer upload
curl -X POST "http://localhost:8000/upload?estado=SP&referencia=2026-01" \
  -F "file=@/tmp/sinapi_sp.xlsx"

# 3. Consultar insumos
curl "http://localhost:8000/insumos?nome=cimento&estado=SP"

# 4. Detalhar composição
curl "http://localhost:8000/composicao?codigo=87316&estado=SP"

# 5. Gerar orçamento
curl "http://localhost:8000/orcamento?itens=C:87316@2.0,I:370@100&estado=SP&regime=NAO_DESONERADO"
```

---

## Links

- 📊 SINAPI Caixa: https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/
- 📘 API Orçamentador (referência): https://www.orcamentador.com.br/api/docs
- 🐙 SDK oficial (PHP): https://github.com/orcamentador/orcamentador-sdk