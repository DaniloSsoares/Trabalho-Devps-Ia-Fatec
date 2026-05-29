"""
apriori.py
----------
Implementação manual do algoritmo Apriori para mineração de regras de associação.

Fluxo:
  1. Gerar itemsets frequentes (suporte >= min_support)
  2. Gerar regras de associação (confiança >= min_confidence)
  3. Calcular lift para cada regra
"""

from itertools import combinations
from typing import Dict, FrozenSet, List, NamedTuple, Set, Tuple


# ─────────────────────────────────────────────
#  Tipos auxiliares
# ─────────────────────────────────────────────

Itemset = FrozenSet[str]


class RegraAssociacao(NamedTuple):
    antecedente: Itemset
    consequente: Itemset
    suporte: float      # P(A ∪ C) / n
    confianca: float    # P(C | A)  = suporte(A ∪ C) / suporte(A)
    lift: float         # confianca / P(C)


# ─────────────────────────────────────────────
#  Funções principais
# ─────────────────────────────────────────────

def _contar_suporte(
    transacoes: List[Set[str]],
    itemsets: List[Itemset],
) -> Dict[Itemset, int]:
    """Conta quantas transações contêm cada itemset."""
    contagem: Dict[Itemset, int] = {is_: 0 for is_ in itemsets}
    for transacao in transacoes:
        for itemset in itemsets:
            if itemset.issubset(transacao):
                contagem[itemset] += 1
    return contagem


def _gerar_candidatos(itemsets_frequentes: List[Itemset], tamanho: int) -> List[Itemset]:
    """
    Gera candidatos de tamanho `tamanho` a partir de itemsets frequentes menores,
    usando a propriedade de fechamento para baixo do Apriori.
    """
    candidatos: Set[Itemset] = set()
    lista = list(itemsets_frequentes)

    for i, a in enumerate(lista):
        for b in lista[i + 1:]:
            uniao = a | b
            if len(uniao) == tamanho:
                candidatos.add(uniao)

    return list(candidatos)


def encontrar_itemsets_frequentes(
    transacoes: List[List[str]],
    min_support: float = 0.05,
) -> Dict[Itemset, float]:
    """
    Executa a etapa de geração de itemsets frequentes do Apriori.

    Args:
        transacoes: Lista de transações (cada uma é uma lista de strings).
        min_support: Suporte mínimo (proporção, 0.0 a 1.0).

    Returns:
        Dicionário {itemset: suporte_relativo}.
    """
    n = len(transacoes)
    min_count = int(min_support * n)

    # Converte para sets para eficiência
    sets_transacoes: List[Set[str]] = [set(t) for t in transacoes]

    # ── Passo 1: itemsets de tamanho 1 ──────────────────────────────────────
    todos_itens: Set[str] = set(item for t in transacoes for item in t)
    candidatos_1 = [frozenset([item]) for item in todos_itens]

    contagem = _contar_suporte(sets_transacoes, candidatos_1)
    frequentes: Dict[Itemset, float] = {}
    frequentes_atuais: List[Itemset] = []

    for itemset, cnt in contagem.items():
        if cnt >= min_count:
            frequentes[itemset] = cnt / n
            frequentes_atuais.append(itemset)

    # ── Passos k > 1: ampliar itemsets ──────────────────────────────────────
    k = 2
    while frequentes_atuais:
        candidatos_k = _gerar_candidatos(frequentes_atuais, k)
        if not candidatos_k:
            break

        contagem_k = _contar_suporte(sets_transacoes, candidatos_k)
        frequentes_atuais = []

        for itemset, cnt in contagem_k.items():
            if cnt >= min_count:
                frequentes[itemset] = cnt / n
                frequentes_atuais.append(itemset)

        k += 1

    return frequentes


def gerar_regras(
    itemsets_frequentes: Dict[Itemset, float],
    min_confidence: float = 0.5,
) -> List[RegraAssociacao]:
    """
    Gera regras de associação a partir dos itemsets frequentes.

    Args:
        itemsets_frequentes: Resultado de `encontrar_itemsets_frequentes`.
        min_confidence: Confiança mínima (0.0 a 1.0).

    Returns:
        Lista de RegraAssociacao ordenada por lift decrescente.
    """
    regras: List[RegraAssociacao] = []

    for itemset, suporte_itemset in itemsets_frequentes.items():
        if len(itemset) < 2:
            continue

        # Gera todas as partições (antecedente → consequente)
        itens = list(itemset)
        for tamanho_ant in range(1, len(itens)):
            for antecedente in combinations(itens, tamanho_ant):
                ant = frozenset(antecedente)
                con = itemset - ant

                suporte_ant = itemsets_frequentes.get(ant, 0.0)
                suporte_con = itemsets_frequentes.get(con, 0.0)

                if suporte_ant == 0 or suporte_con == 0:
                    continue

                confianca = suporte_itemset / suporte_ant
                lift = confianca / suporte_con

                if confianca >= min_confidence:
                    regras.append(RegraAssociacao(
                        antecedente=ant,
                        consequente=con,
                        suporte=suporte_itemset,
                        confianca=confianca,
                        lift=lift,
                    ))

    regras.sort(key=lambda r: r.lift, reverse=True)
    return regras


def resumo_apriori(
    transacoes: List[List[str]],
    min_support: float = 0.05,
    min_confidence: float = 0.4,
) -> Tuple[Dict[Itemset, float], List[RegraAssociacao]]:
    """
    Executa o Apriori completo e retorna itemsets e regras.

    Returns:
        (itemsets_frequentes, regras_de_associacao)
    """
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support)
    regras = gerar_regras(itemsets, min_confidence)
    return itemsets, regras
