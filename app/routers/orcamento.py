from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.services.data import INSUMOS, COMPOSICOES

router = APIRouter(prefix="/orcamento", tags=["Orçamento"])


@router.get("/gerar", summary="Gerar orçamento")
def gerar_orcamento(
    itens: str = Query(
        ...,
        description=(
            "Itens no formato [C|I]:codigo@quantidade separados por vírgula. "
            "C = composição, I = insumo. Ex: C:87316@3.2,I:370@12.5"
        ),
    ),
    estado: str = Query(..., description="Sigla do estado (ex: sp)"),
    regime: Optional[str] = Query(None, description="Regime: DESONERADO ou NAO_DESONERADO"),
    bdi: Optional[float] = Query(None, description="Percentual de BDI a aplicar"),
    data_ref: Optional[str] = Query(None, description="Data de referência"),
    output: Optional[str] = Query(None, description="Formato de saída"),
):
    """
    Gera um orçamento a partir de uma lista de insumos e composições
    com suas respectivas quantidades.

    Formato dos itens: ``[C|I]:codigo@quantidade``

    - **C** = Composição
    - **I** = Insumo

    Exemplo: ``C:87316@3.2,I:370@12.5,I:1379@100``
    """
    estado = estado.lower()
    partes = [p.strip() for p in itens.split(",")]

    resultado = []
    subtotal = 0.0

    for parte in partes:
        try:
            tipo_codigo, qtd_str = parte.split("@")
            tipo_letra, codigo_str = tipo_codigo.split(":")
            tipo_letra = tipo_letra.upper()
            codigo_val = int(codigo_str)
            quantidade = float(qtd_str)
        except (ValueError, IndexError):
            raise HTTPException(
                status_code=400,
                detail=f"Formato inválido para item: '{parte}'. Use [C|I]:codigo@quantidade",
            )

        if tipo_letra == "I":
            item = None
            for ins in INSUMOS:
                if ins["codigo"] == codigo_val:
                    item = ins
                    break
            if item is None:
                raise HTTPException(status_code=404, detail=f"Insumo {codigo_val} não encontrado")
            tipo_nome = "insumo"
        elif tipo_letra == "C":
            item = None
            for comp in COMPOSICOES:
                if comp["codigo"] == codigo_val:
                    item = comp
                    break
            if item is None:
                raise HTTPException(
                    status_code=404, detail=f"Composição {codigo_val} não encontrada"
                )
            tipo_nome = "composicao"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo inválido: '{tipo_letra}'. Use C (composição) ou I (insumo)",
            )

        preco_unitario = item["preco"].get(estado, 0.0)
        preco_total = round(preco_unitario * quantidade, 2)
        subtotal += preco_total

        resultado.append({
            "tipo": tipo_nome,
            "codigo": item["codigo"],
            "nome": item["nome"],
            "unidade": item["unidade"],
            "preco_unitario": preco_unitario,
            "quantidade": quantidade,
            "preco_total": preco_total,
        })

    total_com_bdi = subtotal
    bdi_valor = 0.0
    if bdi is not None and bdi > 0:
        bdi_valor = round(subtotal * bdi / 100, 2)
        total_com_bdi = round(subtotal + bdi_valor, 2)

    return {
        "estado": estado,
        "regime": regime,
        "itens": resultado,
        "subtotal": round(subtotal, 2),
        "bdi_percentual": bdi,
        "bdi_valor": bdi_valor,
        "total": total_com_bdi,
    }
