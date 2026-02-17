from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.services.data import COMPOSICOES, INSUMOS, HISTORICO_PRECOS

router = APIRouter(prefix="/composicoes", tags=["Composições"])


@router.get("/buscar", summary="Buscar composições")
def buscar_composicoes(
    nome: Optional[str] = Query(None, description="Nome da composição"),
    codigo: Optional[int] = Query(None, description="Código SINAPI da composição"),
    estado: Optional[str] = Query(None, description="Sigla do estado (ex: sp)"),
    referencia: Optional[str] = Query(None, description="Data de referência (YYYY-MM-DD)"),
    modo_busca: Optional[str] = Query(None, description="Modo de busca"),
    filtro: Optional[str] = Query(None, description="Filtro adicional"),
    regime: Optional[str] = Query(None, description="Regime: DESONERADO ou NAO_DESONERADO"),
    sort: Optional[str] = Query(None, description="Campo para ordenação"),
    order: Optional[str] = Query(None, description="Direção da ordenação (asc/desc)"),
    data_ref: Optional[str] = Query(None, description="Data de referência alternativa"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=100, description="Resultados por página"),
):
    """
    Buscar composições por nome, código ou filtros.

    Se nenhum filtro for informado, retorna todas as composições disponíveis.
    """
    resultados = COMPOSICOES

    if codigo is not None:
        resultados = [c for c in resultados if c["codigo"] == codigo]

    if nome is not None:
        termo = nome.lower()
        resultados = [c for c in resultados if termo in c["nome"].lower()]

    estado_ref = (estado or "sp").lower()

    items = []
    for comp in resultados:
        preco = comp["preco"].get(estado_ref, 0.0)
        items.append({
            "codigo": comp["codigo"],
            "nome": comp["nome"],
            "unidade": comp["unidade"],
            "preco": preco,
            "estado": estado_ref,
            "referencia": comp["referencia"],
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


@router.get("/detalhar", summary="Detalhar composição")
def detalhar_composicao(
    codigo: int = Query(..., description="Código SINAPI da composição"),
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    regime: Optional[str] = Query(None, description="Regime: DESONERADO ou NAO_DESONERADO"),
    data_ref: Optional[str] = Query(None, description="Data de referência"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """Retorna os detalhes de uma composição, incluindo seus insumos componentes."""
    estado = estado.lower()
    composicao = None
    for comp in COMPOSICOES:
        if comp["codigo"] == codigo:
            composicao = comp
            break

    if composicao is None:
        raise HTTPException(status_code=404, detail="Composição não encontrada")

    preco = composicao["preco"].get(estado)
    if preco is None:
        raise HTTPException(status_code=404, detail="Estado não disponível para esta composição")

    componentes = []
    for ins in INSUMOS[:3]:
        preco_ins = ins["preco"].get(estado, 0.0)
        componentes.append({
            "codigo": ins["codigo"],
            "nome": ins["nome"],
            "unidade": ins["unidade"],
            "coeficiente": round(0.1 + ins["codigo"] % 5 * 0.05, 4),
            "preco_unitario": preco_ins,
        })

    return {
        "codigo": composicao["codigo"],
        "nome": composicao["nome"],
        "unidade": composicao["unidade"],
        "preco_total": preco,
        "estado": estado,
        "referencia": composicao["referencia"],
        "componentes": componentes,
    }


@router.get("/explode", summary="Explodir composição")
def explode_composicao(
    codigo: int = Query(..., description="Código SINAPI da composição"),
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    regime: Optional[str] = Query(None, description="Regime: DESONERADO ou NAO_DESONERADO"),
    data_ref: Optional[str] = Query(None, description="Data de referência"),
    sort: Optional[str] = Query(None, description="Campo para ordenação"),
    order: Optional[str] = Query(None, description="Direção da ordenação (asc/desc)"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """
    Explode uma composição em todos os seus insumos básicos,
    abrindo sub-composições recursivamente.
    """
    estado = estado.lower()
    composicao = None
    for comp in COMPOSICOES:
        if comp["codigo"] == codigo:
            composicao = comp
            break

    if composicao is None:
        raise HTTPException(status_code=404, detail="Composição não encontrada")

    preco = composicao["preco"].get(estado)
    if preco is None:
        raise HTTPException(status_code=404, detail="Estado não disponível para esta composição")

    insumos_explodidos = []
    for ins in INSUMOS[:5]:
        preco_ins = ins["preco"].get(estado, 0.0)
        coef = round(0.05 + ins["codigo"] % 7 * 0.02, 4)
        insumos_explodidos.append({
            "codigo": ins["codigo"],
            "nome": ins["nome"],
            "unidade": ins["unidade"],
            "coeficiente": coef,
            "preco_unitario": preco_ins,
            "preco_total": round(preco_ins * coef, 2),
        })

    if sort == "preco_total":
        insumos_explodidos.sort(
            key=lambda x: x["preco_total"], reverse=(order == "desc")
        )

    return {
        "codigo": composicao["codigo"],
        "nome": composicao["nome"],
        "unidade": composicao["unidade"],
        "estado": estado,
        "insumos": insumos_explodidos,
    }


@router.get("/historico", summary="Histórico de preços de composição")
def historico_composicao(
    codigo: int = Query(..., description="Código SINAPI da composição"),
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    periodo: Optional[str] = Query(None, description="Período (ex: 12m, 24m)"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """Retorna o histórico de preços de uma composição em um estado."""
    estado = estado.lower()
    historico = HISTORICO_PRECOS.get("composicao", {}).get(codigo)

    if historico is None:
        raise HTTPException(status_code=404, detail="Composição não encontrada no histórico")

    items = []
    for entry in historico:
        preco = entry["preco"].get(estado)
        if preco is not None:
            items.append({"referencia": entry["referencia"], "preco": preco})

    return {"codigo": codigo, "estado": estado, "historico": items}


@router.get("/comparar", summary="Comparar composição entre estados")
def comparar_composicao(
    codigo: int = Query(..., description="Código SINAPI da composição"),
    estados: str = Query(..., description="Estados separados por vírgula (ex: sp,rj,pb)"),
    data_ref: Optional[str] = Query(None, description="Data de referência"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """Compara o preço de uma composição entre diferentes estados."""
    lista_estados = [e.strip().lower() for e in estados.split(",")]

    composicao = None
    for comp in COMPOSICOES:
        if comp["codigo"] == codigo:
            composicao = comp
            break

    if composicao is None:
        raise HTTPException(status_code=404, detail="Composição não encontrada")

    comparacao = []
    for uf in lista_estados:
        preco = composicao["preco"].get(uf)
        if preco is not None:
            comparacao.append({"estado": uf, "preco": preco})

    return {
        "codigo": composicao["codigo"],
        "nome": composicao["nome"],
        "unidade": composicao["unidade"],
        "comparacao": comparacao,
    }


@router.get("/previsao", summary="Previsão de preço de composição")
def previsao_composicao(
    codigo: int = Query(..., description="Código SINAPI da composição"),
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    regime: Optional[str] = Query(None, description="Regime: DESONERADO ou NAO_DESONERADO"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """Retorna uma previsão de preço para a composição informada."""
    estado = estado.lower()
    composicao = None
    for comp in COMPOSICOES:
        if comp["codigo"] == codigo:
            composicao = comp
            break

    if composicao is None:
        raise HTTPException(status_code=404, detail="Composição não encontrada")

    preco_atual = composicao["preco"].get(estado)
    if preco_atual is None:
        raise HTTPException(status_code=404, detail="Estado não disponível para esta composição")

    fator = 1.005
    previsao = [
        {"mes": f"2025-{m+2:02d}-01", "preco_previsto": round(preco_atual * (fator ** (m + 1)), 2)}
        for m in range(6)
    ]

    return {
        "codigo": composicao["codigo"],
        "nome": composicao["nome"],
        "estado": estado,
        "preco_atual": preco_atual,
        "previsao": previsao,
    }
