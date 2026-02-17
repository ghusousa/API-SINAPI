# API-SINAPI

API para consulta de insumos e composições da tabela SINAPI, geração de orçamentos, indicadores econômicos, estados e encargos sociais.

## Uso

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# Swagger UI em /api/docs
```

## Testes

```bash
pip install pytest httpx
pytest tests/
```