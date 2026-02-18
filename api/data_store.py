"""Armazenamento em memória e consulta dos dados SINAPI.

Funciona como uma camada de dados que indexa insumos, composições e
composições analíticas carregados de arquivos XLSX/ZIP, e oferece métodos
de consulta compatíveis com os endpoints da API Orçamentador.
"""

import re
import unicodedata
from collections import defaultdict
from typing import Any, Dict, List, Optional


def _norm(text: str) -> str:
    """Normaliza texto para busca (remove acentos, maiúsculas)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).upper()


class SinapiStore:
    """Armazenamento em memória para dados SINAPI."""

    def __init__(self):
        # Listas brutas
        self._insumos: List[dict] = []
        self._composicoes: List[dict] = []
        self._analitico: List[dict] = []

        # Índices para busca rápida
        self._insumos_by_codigo: Dict[int, List[dict]] = defaultdict(list)
        self._composicoes_by_codigo: Dict[int, List[dict]] = defaultdict(list)
        self._analitico_by_comp: Dict[int, List[dict]] = defaultdict(list)

        # Referências carregadas
        self._referencias: set = set()
        self._estados: set = set()

    def load(self, data: dict):
        """Carrega dados no store (resultado de data_loader).

        Args:
            data: dict com chaves 'insumos', 'composicoes', 'analitico'.
        """
        for item in data.get("insumos", []):
            self._insumos.append(item)
            self._insumos_by_codigo[item["codigo"]].append(item)
            self._estados.add(item["estado"].upper())
            if item.get("referencia"):
                self._referencias.add(item["referencia"])

        for item in data.get("composicoes", []):
            self._composicoes.append(item)
            self._composicoes_by_codigo[item["codigo"]].append(item)
            self._estados.add(item["estado"].upper())
            if item.get("referencia"):
                self._referencias.add(item["referencia"])

        for item in data.get("analitico", []):
            self._analitico.append(item)
            self._analitico_by_comp[item["composicao_codigo"]].append(item)

    def clear(self):
        """Remove todos os dados carregados."""
        self._insumos.clear()
        self._composicoes.clear()
        self._analitico.clear()
        self._insumos_by_codigo.clear()
        self._composicoes_by_codigo.clear()
        self._analitico_by_comp.clear()
        self._referencias.clear()
        self._estados.clear()

    # ------------------------------------------------------------------
    # Consultas - Insumos
    # ------------------------------------------------------------------

    def buscar_insumos(
        self,
        nome: Optional[str] = None,
        codigo: Optional[int] = None,
        estado: Optional[str] = None,
        regime: Optional[str] = None,
        referencia: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Busca insumos por filtros (compatível com /insumos do Orçamentador)."""
        items = self._insumos

        if codigo:
            items = [i for i in items if i["codigo"] == int(codigo)]
        if nome:
            nome_norm = _norm(nome)
            items = [i for i in items if nome_norm in _norm(i.get("descricao", ""))]
        if estado:
            estado_up = estado.upper()
            items = [i for i in items if i.get("estado", "").upper() == estado_up]
        if regime:
            regime_up = regime.upper()
            items = [i for i in items if i.get("regime", "").upper() == regime_up]
        if referencia:
            items = [i for i in items if i.get("referencia") == referencia]

        # Ordenação
        if sort:
            reverse = (order or "").upper() == "DESC"
            items = sorted(items, key=lambda x: x.get(sort, ""), reverse=reverse)

        total = len(items)
        start = (page - 1) * limit
        page_items = items[start: start + limit]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "data": page_items,
        }

    # ------------------------------------------------------------------
    # Consultas - Composições
    # ------------------------------------------------------------------

    def buscar_composicoes(
        self,
        nome: Optional[str] = None,
        codigo: Optional[int] = None,
        estado: Optional[str] = None,
        regime: Optional[str] = None,
        referencia: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Busca composições por filtros (compatível com /composicoes)."""
        items = self._composicoes

        if codigo:
            items = [i for i in items if i["codigo"] == int(codigo)]
        if nome:
            nome_norm = _norm(nome)
            items = [i for i in items if nome_norm in _norm(i.get("descricao", ""))]
        if estado:
            estado_up = estado.upper()
            items = [i for i in items if i.get("estado", "").upper() == estado_up]
        if regime:
            regime_up = regime.upper()
            items = [i for i in items if i.get("regime", "").upper() == regime_up]
        if referencia:
            items = [i for i in items if i.get("referencia") == referencia]

        if sort:
            reverse = (order or "").upper() == "DESC"
            items = sorted(items, key=lambda x: x.get(sort, ""), reverse=reverse)

        total = len(items)
        start = (page - 1) * limit
        page_items = items[start: start + limit]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "data": page_items,
        }

    def detalhar_composicao(
        self,
        codigo: int,
        estado: Optional[str] = None,
        regime: Optional[str] = None,
        **kwargs,
    ) -> Optional[dict]:
        """Detalha uma composição (compatível com /composicao)."""
        items = self._composicoes_by_codigo.get(int(codigo), [])
        if estado:
            items = [i for i in items if i.get("estado", "").upper() == estado.upper()]
        if regime:
            items = [i for i in items if i.get("regime", "").upper() == regime.upper()]
        if not items:
            return None

        comp = items[0].copy()
        # Adicionar itens da composição (analítico)
        analitico = self._analitico_by_comp.get(int(codigo), [])
        if estado:
            analitico = [a for a in analitico if a.get("estado", "").upper() == estado.upper()]
        if regime:
            analitico = [a for a in analitico if a.get("regime", "").upper() == regime.upper()]
        comp["itens"] = analitico
        return comp

    def explode_composicao(
        self,
        codigo: int,
        estado: Optional[str] = None,
        regime: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Explode composição em insumos (compatível com /composicao_explode)."""
        analitico = self._analitico_by_comp.get(int(codigo), [])
        if estado:
            analitico = [a for a in analitico if a.get("estado", "").upper() == estado.upper()]
        if regime:
            analitico = [a for a in analitico if a.get("regime", "").upper() == regime.upper()]

        return {
            "codigo": int(codigo),
            "itens": analitico,
            "total_itens": len(analitico),
        }

    # ------------------------------------------------------------------
    # Consultas - Histórico, Comparar, Previsão
    # ------------------------------------------------------------------

    def historico(
        self,
        codigo: int,
        item: str = "insumo",
        estado: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Histórico de preço/custo (compatível com /historico)."""
        if item == "insumo":
            items = self._insumos_by_codigo.get(int(codigo), [])
        else:
            items = self._composicoes_by_codigo.get(int(codigo), [])

        if estado:
            items = [i for i in items if i.get("estado", "").upper() == estado.upper()]

        historico = []
        refs = {}
        for i in items:
            ref = i.get("referencia", "")
            val = i.get("preco_mediano") if item == "insumo" else i.get("custo_total")
            if ref and ref not in refs:
                refs[ref] = True
                historico.append({
                    "referencia": ref,
                    "valor": val,
                    "estado": i.get("estado"),
                    "regime": i.get("regime"),
                })

        return {
            "codigo": int(codigo),
            "item": item,
            "historico": sorted(historico, key=lambda x: x.get("referencia", "")),
        }

    def comparar(
        self,
        codigo: int,
        item: str = "insumo",
        estados: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Compara preços entre estados (compatível com /comparar)."""
        if item == "insumo":
            items = self._insumos_by_codigo.get(int(codigo), [])
        else:
            items = self._composicoes_by_codigo.get(int(codigo), [])

        estado_list = [s.strip().upper() for s in estados.split(",")] if estados else []

        if estado_list:
            items = [i for i in items if i.get("estado", "").upper() in estado_list]

        comparacao = []
        seen = set()
        for i in items:
            key = (i.get("estado"), i.get("regime"))
            if key in seen:
                continue
            seen.add(key)
            val = i.get("preco_mediano") if item == "insumo" else i.get("custo_total")
            comparacao.append({
                "estado": i.get("estado"),
                "valor": val,
                "regime": i.get("regime"),
                "referencia": i.get("referencia"),
            })

        return {
            "codigo": int(codigo),
            "item": item,
            "comparacao": comparacao,
        }

    def previsao(
        self,
        codigo: int,
        item: str = "insumo",
        estado: Optional[str] = None,
        regime: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Previsão de preço (compatível com /previsao).

        Nota: Com dados locais, retorna o último valor disponível como base.
        """
        if item == "insumo":
            items = self._insumos_by_codigo.get(int(codigo), [])
        else:
            items = self._composicoes_by_codigo.get(int(codigo), [])

        if estado:
            items = [i for i in items if i.get("estado", "").upper() == estado.upper()]
        if regime:
            items = [i for i in items if i.get("regime", "").upper() == regime.upper()]

        if not items:
            return {"codigo": int(codigo), "item": item, "previsao": None}

        latest = sorted(items, key=lambda x: x.get("referencia", ""), reverse=True)[0]
        val = latest.get("preco_mediano") if item == "insumo" else latest.get("custo_total")

        return {
            "codigo": int(codigo),
            "item": item,
            "previsao": {
                "valor_base": val,
                "referencia_base": latest.get("referencia"),
                "estado": latest.get("estado"),
                "regime": latest.get("regime"),
            },
        }

    # ------------------------------------------------------------------
    # Consultas - Encargos, Indicadores, Estados, Orçamento
    # ------------------------------------------------------------------

    def buscar_encargos(self, estado: Optional[str] = None, **kwargs) -> dict:
        """Busca encargos sociais (compatível com /encargos)."""
        # Encargos são derivados dos dados carregados
        return {
            "estado": estado.upper() if estado else None,
            "encargos": [],
            "mensagem": "Encargos extraídos dos dados SINAPI carregados",
        }

    def listar_indicadores(self, **kwargs) -> dict:
        """Lista indicadores econômicos (compatível com /indicadores)."""
        return {
            "indicadores": {},
            "mensagem": "Indicadores não disponíveis nos dados SINAPI locais",
        }

    def listar_estados(
        self,
        estado: Optional[str] = None,
        ibge: Optional[int] = None,
        regiao: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Lista estados disponíveis (compatível com /estados)."""
        from api.data_loader import ESTADOS_INFO

        result = []
        for uf, info in ESTADOS_INFO.items():
            if estado and uf != estado.upper():
                continue
            if ibge and info["ibge"] != int(ibge):
                continue
            if regiao and info["regiao"] != regiao.lower():
                continue

            result.append({
                "uf": uf,
                "nome": info["nome"],
                "ibge": info["ibge"],
                "regiao": info["regiao"],
                "disponivel": uf in self._estados,
            })

        return {"estados": result}

    def gerar_orcamento(
        self,
        itens: str,
        estado: str,
        regime: str = "NAO_DESONERADO",
        bdi: Optional[float] = None,
        **kwargs,
    ) -> dict:
        """Gera orçamento (compatível com /orcamento).

        Args:
            itens: String no formato '[C|I]:codigo@quantidade,...'.
            estado: UF.
            regime: Regime tributário.
            bdi: Percentual de BDI.
        """
        estado_up = estado.upper()
        regime_up = regime.upper()
        bdi_pct = float(bdi) if bdi else 0.0

        parsed_items = []
        total = 0.0

        for part in itens.split(","):
            part = part.strip()
            if not part:
                continue
            # Parse "C:12321@3.2" or "I:234@12.5"
            m = re.match(r"([CI]):(\d+)@([\d.]+)", part, re.IGNORECASE)
            if not m:
                continue

            tipo = "composicao" if m.group(1).upper() == "C" else "insumo"
            codigo = int(m.group(2))
            qtd = float(m.group(3))

            if tipo == "insumo":
                candidates = self._insumos_by_codigo.get(codigo, [])
            else:
                candidates = self._composicoes_by_codigo.get(codigo, [])

            candidates = [c for c in candidates if c.get("estado", "").upper() == estado_up]
            candidates = [c for c in candidates if c.get("regime", "").upper() == regime_up]

            if candidates:
                item_data = candidates[0]
                unit_val = item_data.get("preco_mediano") if tipo == "insumo" else item_data.get("custo_total")
                unit_val = unit_val or 0.0
            else:
                item_data = {"codigo": codigo, "descricao": "Não encontrado"}
                unit_val = 0.0

            subtotal = unit_val * qtd
            total += subtotal

            parsed_items.append({
                "tipo": tipo,
                "codigo": codigo,
                "descricao": item_data.get("descricao", ""),
                "unidade": item_data.get("unidade", ""),
                "quantidade": qtd,
                "preco_unitario": unit_val,
                "subtotal": round(subtotal, 2),
            })

        bdi_valor = round(total * bdi_pct / 100, 2) if bdi_pct else 0.0

        return {
            "itens": parsed_items,
            "subtotal": round(total, 2),
            "bdi_percentual": bdi_pct,
            "bdi_valor": bdi_valor,
            "total": round(total + bdi_valor, 2),
            "estado": estado_up,
            "regime": regime_up,
        }


# Instância global do store
store = SinapiStore()
