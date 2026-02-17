# API SINAPI – Sistema de Orçamento

API REST para consulta de insumos e composições da tabela **SINAPI** (Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil), geração de orçamentos, indicadores econômicos, estados e encargos sociais.

Inspirada na [API do Orcamentador](https://orcamentador.com.br/api/docs).

---

## 🚀 Início Rápido

### Requisitos

- Python ≥ 3.10

### Instalação

```bash
pip install -r requirements.txt
```

### Executar

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`.  
Documentação interativa (Swagger): `http://127.0.0.1:8000/api/docs`

### Testes

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## 📚 Endpoints

### Insumos

| Método | Endpoint              | Descrição                                |
|--------|-----------------------|------------------------------------------|
| GET    | `/insumos/buscar`     | Buscar insumos por nome, código ou filtro |
| GET    | `/insumos/historico`  | Histórico de preços de um insumo          |
| GET    | `/insumos/comparar`   | Comparar preço de insumo entre estados    |
| GET    | `/insumos/previsao`   | Previsão de preço de um insumo            |

### Composições

| Método | Endpoint                  | Descrição                                 |
|--------|---------------------------|-------------------------------------------|
| GET    | `/composicoes/buscar`     | Buscar composições por nome ou código     |
| GET    | `/composicoes/detalhar`   | Detalhar composição com seus componentes  |
| GET    | `/composicoes/explode`    | Explodir composição em insumos básicos    |
| GET    | `/composicoes/historico`  | Histórico de preços de uma composição     |
| GET    | `/composicoes/comparar`   | Comparar preço entre estados              |
| GET    | `/composicoes/previsao`   | Previsão de preço de uma composição       |

### Orçamento

| Método | Endpoint            | Descrição                                      |
|--------|---------------------|-------------------------------------------------|
| GET    | `/orcamento/gerar`  | Gerar orçamento a partir de insumos/composições |

### Estados

| Método | Endpoint           | Descrição                      |
|--------|--------------------|--------------------------------|
| GET    | `/estados/listar`  | Listar estados disponíveis     |

### Indicadores

| Método | Endpoint               | Descrição                         |
|--------|------------------------|-----------------------------------|
| GET    | `/indicadores/listar`  | Listar indicadores econômicos     |

### Encargos

| Método | Endpoint            | Descrição                        |
|--------|---------------------|----------------------------------|
| GET    | `/encargos/buscar`  | Buscar encargos sociais por estado|

---

## 💡 Exemplo de Uso

### Gerar orçamento

```
GET /orcamento/gerar?itens=C:87316@3.2,I:370@12.5&estado=sp&bdi=25
```

Formato dos itens: `[C|I]:codigo@quantidade`
- **C** = Composição
- **I** = Insumo

---

## 📂 Estrutura do Projeto

```
app/
├── main.py              # Aplicação FastAPI
├── routers/
│   ├── insumos.py       # Rotas de insumos
│   ├── composicoes.py   # Rotas de composições
│   ├── orcamento.py     # Rotas de orçamento
│   ├── estados.py       # Rotas de estados
│   ├── indicadores.py   # Rotas de indicadores
│   └── encargos.py      # Rotas de encargos
├── schemas/             # Modelos Pydantic
├── services/
│   └── data.py          # Dados de exemplo (SINAPI)
└── middleware/
tests/
└── test_api.py          # Testes automatizados
```

---

## 📄 Licença

MIT