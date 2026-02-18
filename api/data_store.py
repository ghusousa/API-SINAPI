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

        Remove dados antigos do mesmo estado/referência/regime antes de
        inserir os novos, evitando duplicação em uploads repetidos.

        Args:
            data: dict com chaves 'insumos', 'composicoes', 'analitico'.
        """
        # Identifica combinações (estado, referencia, regime) dos novos dados
        # para remover duplicatas existentes antes de inserir.
        new_keys: set = set()
        for item in data.get("insumos", []) + data.get("composicoes", []):
            new_keys.add((
                item.get("estado", "").upper(),
                item.get("referencia", ""),
                item.get("regime", "").upper(),
            ))

        if new_keys:
            self._remove_matching(new_keys)

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

    def _remove_matching(self, keys: set):
        """Remove dados existentes que correspondem às chaves (estado, ref, regime)."""

        def _match(item: dict) -> bool:
            return (
                item.get("estado", "").upper(),
                item.get("referencia", ""),
                item.get("regime", "").upper(),
            ) in keys

        # Filtrar listas
        self._insumos = [i for i in self._insumos if not _match(i)]
        self._composicoes = [c for c in self._composicoes if not _match(c)]
        self._analitico = [a for a in self._analitico if not _match(a)]

        # Reconstruir índices
        self._insumos_by_codigo.clear()
        for item in self._insumos:
            self._insumos_by_codigo[item["codigo"]].append(item)

        self._composicoes_by_codigo.clear()
        for item in self._composicoes:
            self._composicoes_by_codigo[item["codigo"]].append(item)

        self._analitico_by_comp.clear()
        for item in self._analitico:
            self._analitico_by_comp[item["composicao_codigo"]].append(item)

        # Recalcular estados/referências
        self._estados = {i["estado"].upper() for i in self._insumos + self._composicoes}
        self._referencias = {
            i["referencia"] for i in self._insumos + self._composicoes
            if i.get("referencia")
        }

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
    # Helpers - merge items from different regimes
    # ------------------------------------------------------------------

    def _merge_insumo_prices(self, items: List[dict]) -> List[dict]:
        """Merge insumo items with same codigo+estado+referencia into one with both prices."""
        merged: Dict[tuple, dict] = {}
        for i in items:
            key = (i["codigo"], i.get("estado", ""), i.get("referencia", ""))
            if key not in merged:
                merged[key] = {
                    "codigo": i["codigo"],
                    "nome": i.get("nome", ""),
                    "unidade": i.get("unidade", ""),
                    "preco_desonerado": None,
                    "preco_naodesonerado": None,
                    "tipo": i.get("tipo"),
                    "classe": i.get("classe"),
                    "referencia": i.get("referencia"),
                }
            regime = i.get("regime", "").upper()
            preco = i.get("preco")
            if regime == "DESONERADO":
                merged[key]["preco_desonerado"] = preco
            else:
                merged[key]["preco_naodesonerado"] = preco
        return list(merged.values())

    def _merge_composicao_prices(self, items: List[dict]) -> List[dict]:
        """Merge composicao items with same codigo+estado+referencia into one with both prices."""
        merged: Dict[tuple, dict] = {}
        for i in items:
            key = (i["codigo"], i.get("estado", ""), i.get("referencia", ""))
            if key not in merged:
                merged[key] = {
                    "codigo": i["codigo"],
                    "nome": i.get("nome", ""),
                    "unidade": i.get("unidade", ""),
                    "preco_desonerado": None,
                    "preco_naodesonerado": None,
                    "referencia": i.get("referencia"),
                }
            regime = i.get("regime", "").upper()
            preco = i.get("preco")
            if regime == "DESONERADO":
                merged[key]["preco_desonerado"] = preco
            else:
                merged[key]["preco_naodesonerado"] = preco
        return list(merged.values())

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
            items = [i for i in items if nome_norm in _norm(i.get("nome", ""))]
        if estado:
            estado_up = estado.upper()
            items = [i for i in items if i.get("estado", "").upper() == estado_up]
        if regime:
            regime_up = regime.upper()
            items = [i for i in items if i.get("regime", "").upper() == regime_up]
        if referencia:
            items = [i for i in items if i.get("referencia") == referencia]

        # Merge prices from different regimes
        merged = self._merge_insumo_prices(items)

        # Ordenação
        if sort:
            reverse = (order or "").upper() == "DESC"
            merged = sorted(merged, key=lambda x: x.get(sort, ""), reverse=reverse)

        total = len(merged)
        start = (page - 1) * limit
        page_items = merged[start: start + limit]

        return {
            "data": page_items,
            "total": total,
            "page": page,
            "limit": limit,
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
            items = [i for i in items if nome_norm in _norm(i.get("nome", ""))]
        if estado:
            estado_up = estado.upper()
            items = [i for i in items if i.get("estado", "").upper() == estado_up]
        if regime:
            regime_up = regime.upper()
            items = [i for i in items if i.get("regime", "").upper() == regime_up]
        if referencia:
            items = [i for i in items if i.get("referencia") == referencia]

        # Merge prices from different regimes
        merged = self._merge_composicao_prices(items)

        if sort:
            reverse = (order or "").upper() == "DESC"
            merged = sorted(merged, key=lambda x: x.get(sort, ""), reverse=reverse)

        total = len(merged)
        start = (page - 1) * limit
        page_items = merged[start: start + limit]

        return {
            "data": page_items,
            "total": total,
            "page": page,
            "limit": limit,
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

        # Merge prices from both regimes
        all_items = self._composicoes_by_codigo.get(int(codigo), [])
        if estado:
            all_items = [i for i in all_items if i.get("estado", "").upper() == estado.upper()]
        merged = self._merge_composicao_prices(all_items)
        comp = merged[0].copy() if merged else items[0].copy()

        # Adicionar itens da composição (analítico)
        analitico = self._analitico_by_comp.get(int(codigo), [])
        if estado:
            analitico = [a for a in analitico if a.get("estado", "").upper() == estado.upper()]
        if regime:
            analitico = [a for a in analitico if a.get("regime", "").upper() == regime.upper()]

        # Format analítico items with nome, preco_unitario, preco_total
        formatted_items = []
        for a in analitico:
            coef = a.get("coeficiente", 0) or 0
            pu = a.get("preco_unitario") or 0
            formatted_items.append({
                "codigo": a.get("item_codigo"),
                "nome": a.get("nome", ""),
                "unidade": a.get("unidade", ""),
                "coeficiente": coef,
                "preco_unitario": a.get("preco_unitario"),
                "preco_total": round(coef * pu, 2),
            })

        comp["itens"] = formatted_items
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

        formatted_items = []
        for a in analitico:
            coef = a.get("coeficiente", 0) or 0
            pu = a.get("preco_unitario") or 0
            formatted_items.append({
                "codigo": a.get("item_codigo"),
                "nome": a.get("nome", ""),
                "unidade": a.get("unidade", ""),
                "coeficiente": coef,
                "preco_unitario": a.get("preco_unitario"),
                "preco_total": round(coef * pu, 2),
            })

        return {
            "codigo": int(codigo),
            "itens": formatted_items,
            "total_itens": len(formatted_items),
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
            val = i.get("preco")
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
            val = i.get("preco")
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
        val = latest.get("preco")

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
    ) -> list:
        """Lista estados disponíveis (compatível com /estados). Returns flat list."""
        from api.data_loader import ESTADOS_INFO

        result = []
        for uf, info in ESTADOS_INFO.items():
            if estado and uf != estado.upper():
                continue
            if ibge and info["ibge"] != int(ibge):
                continue
            if regiao and info["regiao"] != regiao.upper():
                continue

            result.append({
                "uf": uf,
                "nome": info["nome"],
                "ibge": info["ibge"],
                "regiao": info["regiao"],
            })

        return result

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

        from api.data_loader import ESTADOS_INFO
        estado_info = ESTADOS_INFO.get(estado_up, {})
        estado_label = f"{estado_info.get('nome', estado_up)} ({estado_up})"

        parsed_items = []
        total_insumos = 0.0

        for part in itens.split(","):
            part = part.strip()
            if not part:
                continue
            m = re.match(r"([CI]):(\d+)@([\d.]+)", part, re.IGNORECASE)
            if not m:
                continue

            tipo_key = m.group(1).upper()
            tipo_label = "Composição" if tipo_key == "C" else "Insumo"
            tipo_source = "composicao" if tipo_key == "C" else "insumo"
            codigo = int(m.group(2))
            qtd = float(m.group(3))

            if tipo_source == "insumo":
                candidates = self._insumos_by_codigo.get(codigo, [])
            else:
                candidates = self._composicoes_by_codigo.get(codigo, [])

            candidates = [c for c in candidates if c.get("estado", "").upper() == estado_up]
            candidates = [c for c in candidates if c.get("regime", "").upper() == regime_up]

            if candidates:
                item_data = candidates[0]
                unit_val = item_data.get("preco") or 0.0
            else:
                item_data = {"codigo": codigo, "nome": "Não encontrado"}
                unit_val = 0.0

            subtotal = unit_val * qtd
            total_insumos += subtotal

            parsed_items.append({
                "tipo": tipo_label,
                "codigo": codigo,
                "nome": item_data.get("nome", ""),
                "quantidade": qtd,
                "preco_unit": unit_val,
                "subtotal": round(subtotal, 2),
            })

        total_geral = round(total_insumos + (total_insumos * bdi_pct / 100), 2) if bdi_pct else round(total_insumos, 2)

        return {
            "totais": {
                "total_insumos": round(total_insumos, 2),
                "total_geral": total_geral,
                "bdi_percentual": bdi_pct,
                "regime": regime_up,
                "estado": estado_label,
            },
            "itens": parsed_items,
        }


# Instância global do store
store = SinapiStore()
