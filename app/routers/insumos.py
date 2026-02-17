from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

from app.services.data import INSUMOS, HISTORICO_PRECOS

router = APIRouter(prefix="/insumos", tags=["Insumos"])


@router.get("/buscar", summary="Buscar insumos")
def buscar_insumos(
    nome: Optional[str] = Query(None, description="Nome do insumo"),
    codigo: Optional[int] = Query(None, description="Código SINAPI do insumo"),
    estado: Optional[str] = Query(None, description="Sigla do estado (ex: sp)"),
    referencia: Optional[str] = Query(None, description="Data de referência (YYYY-MM-DD)"),
    modo_busca: Optional[str] = Query(None, description="Modo de busca"),
    tipo: Optional[str] = Query(None, description="Tipo do insumo"),
    familia: Optional[str] = Query(None, description="Família do insumo"),
    regime: Optional[str] = Query(None, description="Regime: DESONERADO ou NAO_DESONERADO"),
    sort: Optional[str] = Query(None, description="Campo para ordenação"),
    order: Optional[str] = Query(None, description="Direção da ordenação (asc/desc)"),
    data_ref: Optional[str] = Query(None, description="Data de referência alternativa"),
    detail: Optional[bool] = Query(None, description="Incluir detalhes"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=100, description="Resultados por página"),
):
    """
    Buscar insumos por nome, código ou filtros.

    Se nenhum filtro for informado, retorna todos os insumos disponíveis.
    """
    resultados = INSUMOS

    if codigo is not None:
        resultados = [i for i in resultados if i["codigo"] == codigo]

    if nome is not None:
        termo = nome.lower()
        resultados = [i for i in resultados if termo in i["nome"].lower()]

    estado_ref = (estado or "sp").lower()

    items = []
    for ins in resultados:
        preco = ins["preco"].get(estado_ref, 0.0)
        items.append({
            "codigo": ins["codigo"],
            "nome": ins["nome"],
            "unidade": ins["unidade"],
            "preco": preco,
            "estado": estado_ref,
            "referencia": ins["referencia"],
        })

    if sort == "preco":
        items.sort(key=lambda x: x["preco"], reverse=(order == "desc"))
    elif sort == "codigo":
        items.sort(key=lambda x: x["codigo"], reverse=(order == "desc"))

    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    items = items[start:end]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "resultados": items,
    }


@router.get("/historico", summary="Histórico de preços de insumo")
def historico_insumo(
    codigo: int = Query(..., description="Código SINAPI do insumo"),
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    periodo: Optional[str] = Query(None, description="Período (ex: 12m, 24m)"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """Retorna o histórico de preços de um insumo em um estado."""
    estado = estado.lower()
    historico = HISTORICO_PRECOS.get("insumo", {}).get(codigo)

    if historico is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado no histórico")

    items = []
    for entry in historico:
        preco = entry["preco"].get(estado)
        if preco is not None:
            items.append({"referencia": entry["referencia"], "preco": preco})

    return {"codigo": codigo, "estado": estado, "historico": items}


@router.get("/comparar", summary="Comparar insumo entre estados")
def comparar_insumo(
    codigo: int = Query(..., description="Código SINAPI do insumo"),
    estados: str = Query(..., description="Estados separados por vírgula (ex: sp,rj,pb)"),
    data_ref: Optional[str] = Query(None, description="Data de referência"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """Compara o preço de um insumo entre diferentes estados."""
    lista_estados = [e.strip().lower() for e in estados.split(",")]

    insumo = None
    for ins in INSUMOS:
        if ins["codigo"] == codigo:
            insumo = ins
            break

    if insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")

    comparacao = []
    for uf in lista_estados:
        preco = insumo["preco"].get(uf)
        if preco is not None:
            comparacao.append({"estado": uf, "preco": preco})

    return {
        "codigo": insumo["codigo"],
        "nome": insumo["nome"],
        "unidade": insumo["unidade"],
        "comparacao": comparacao,
    }


@router.get("/previsao", summary="Previsão de preço de insumo")
def previsao_insumo(
    codigo: int = Query(..., description="Código SINAPI do insumo"),
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    regime: Optional[str] = Query(None, description="Regime: DESONERADO ou NAO_DESONERADO"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """Retorna uma previsão de preço para o insumo informado."""
    estado = estado.lower()
    insumo = None
    for ins in INSUMOS:
        if ins["codigo"] == codigo:
            insumo = ins
            break

    if insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")

    preco_atual = insumo["preco"].get(estado)
    if preco_atual is None:
        raise HTTPException(status_code=404, detail="Estado não disponível para este insumo")

    fator = 1.005
    previsao = [
        {"mes": f"2025-0{m+2}-01", "preco_previsto": round(preco_atual * (fator ** (m + 1)), 2)}
        for m in range(6)
    ]

    return {
        "codigo": insumo["codigo"],
        "nome": insumo["nome"],
        "estado": estado,
        "preco_atual": preco_atual,
        "previsao": previsao,
    }
