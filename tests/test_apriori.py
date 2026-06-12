"""
test_apriori.py
---------------
Testes do algoritmo Apriori: geração de itemsets frequentes e regras.
Usa datasets pequenos com resultados calculáveis à mão.
"""

from apriori import (
    encontrar_itemsets_frequentes,
    gerar_regras,
    resumo_apriori,
)


# ─────────────────────────────────────────────
#  Itemsets frequentes
# ─────────────────────────────────────────────

def test_itemset_unico_frequente():
    """Um item presente em todas as transações tem suporte 1.0."""
    transacoes = [["a"], ["a"], ["a"], ["a"]]
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.5)

    assert frozenset(["a"]) in itemsets
    assert itemsets[frozenset(["a"])] == 1.0


def test_suporte_relativo_correto():
    """O suporte deve ser a fração de transações que contêm o itemset."""
    # 'a' aparece em 3 de 4 transações -> suporte 0.75
    transacoes = [["a", "b"], ["a", "c"], ["a"], ["b"]]
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.5)

    assert itemsets[frozenset(["a"])] == 0.75


def test_item_infrequente_eh_podado():
    """Itens abaixo do suporte mínimo não devem aparecer."""
    # 'raro' aparece em 1 de 4 -> suporte 0.25 < 0.5
    transacoes = [["a"], ["a"], ["a"], ["raro"]]
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.5)

    assert frozenset(["raro"]) not in itemsets


def test_itemset_pareado():
    """Pares frequentes devem ser detectados (propriedade Apriori)."""
    transacoes = [
        ["arroz", "feijão"],
        ["arroz", "feijão"],
        ["arroz", "feijão"],
        ["arroz"],
    ]
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.5)

    assert frozenset(["arroz", "feijão"]) in itemsets
    assert itemsets[frozenset(["arroz", "feijão"])] == 0.75


def test_fechamento_para_baixo():
    """Se um par é frequente, seus subconjuntos também devem ser."""
    transacoes = [["a", "b", "c"]] * 5
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.5)

    # O trio frequente implica que todos os pares e singletons existem
    assert frozenset(["a", "b", "c"]) in itemsets
    for sub in (["a"], ["b"], ["c"], ["a", "b"], ["a", "c"], ["b", "c"]):
        assert frozenset(sub) in itemsets


def test_dataset_vazio_nao_quebra():
    """Transações vazias não devem gerar erro."""
    itemsets = encontrar_itemsets_frequentes([[], [], []], min_support=0.5)
    assert itemsets == {}


# ─────────────────────────────────────────────
#  Regras de associação
# ─────────────────────────────────────────────

def test_regra_confianca_total():
    """Quando A sempre acompanha B, confiança(A->B) = 1.0."""
    transacoes = [["a", "b"]] * 4
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.5)
    regras = gerar_regras(itemsets, min_confidence=0.5)

    assert regras  # deve haver pelo menos uma regra
    for r in regras:
        assert 0.0 <= r.confianca <= 1.0001
    assert any(r.confianca == 1.0 for r in regras)


def test_regras_ordenadas_por_lift():
    """As regras devem vir ordenadas por lift decrescente."""
    transacoes = [
        ["a", "b"], ["a", "b"], ["a", "b"],
        ["a", "c"], ["c"], ["b"],
    ]
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.3)
    regras = gerar_regras(itemsets, min_confidence=0.1)

    lifts = [r.lift for r in regras]
    assert lifts == sorted(lifts, reverse=True)


def test_confianca_minima_filtra():
    """Regras abaixo da confiança mínima não devem ser retornadas."""
    transacoes = [["a", "b"], ["a", "b"], ["a"], ["a"]]
    itemsets = encontrar_itemsets_frequentes(transacoes, min_support=0.4)
    regras = gerar_regras(itemsets, min_confidence=0.99)

    # confiança(a->b) = 0.5, abaixo de 0.99 -> nenhuma regra
    assert all(r.confianca >= 0.99 for r in regras)


# ─────────────────────────────────────────────
#  Pipeline completo
# ─────────────────────────────────────────────

def test_resumo_apriori_retorna_tupla():
    transacoes = [["a", "b"], ["a", "b"], ["a"]]
    itemsets, regras = resumo_apriori(transacoes, min_support=0.5, min_confidence=0.5)

    assert isinstance(itemsets, dict)
    assert isinstance(regras, list)
