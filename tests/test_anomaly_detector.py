"""
test_anomaly_detector.py
------------------------
Testes do cálculo de score de anomalia, detecção e métricas de avaliação.
"""

import pytest

from anomaly_detector import (
    calcular_score_anomalia,
    detectar_anomalias,
    avaliar_deteccao,
)


# ─────────────────────────────────────────────
#  Score de anomalia
# ─────────────────────────────────────────────

def test_score_maximo_sem_padrao_conhecido():
    """Itens não reconhecidos -> score 1.0 (anomalia máxima)."""
    score = calcular_score_anomalia(["caviar", "trufa"], itemsets_frequentes={})
    assert score == 1.0


def test_score_baixo_para_itemset_frequente():
    """Itens de alto suporte -> score baixo."""
    itemsets = {frozenset(["arroz"]): 0.9, frozenset(["feijão"]): 0.8}
    score = calcular_score_anomalia(["arroz", "feijão"], itemsets)

    # suporte médio = 0.85 -> score = 0.15
    assert score == pytest.approx(0.15, abs=1e-6)


def test_score_entre_zero_e_um():
    """O score deve sempre estar no intervalo [0, 1]."""
    itemsets = {frozenset(["x"]): 0.5}
    for itens in (["x"], ["x", "y"], ["y", "z"], []):
        score = calcular_score_anomalia(itens, itemsets)
        assert 0.0 <= score <= 1.0


def test_score_ignora_itens_duplicados():
    """Itens repetidos não devem alterar o score."""
    itemsets = {frozenset(["a"]): 0.6}
    assert calcular_score_anomalia(["a", "a", "a"], itemsets) == \
        calcular_score_anomalia(["a"], itemsets)


# ─────────────────────────────────────────────
#  Detecção por threshold
# ─────────────────────────────────────────────

def test_detectar_anomalias_separa_outlier():
    """Uma transação claramente atípica deve ser detectada."""
    itemsets = {frozenset(["arroz"]): 0.9, frozenset(["feijão"]): 0.9}
    transacoes = [
        {"id": 1, "itens": ["arroz", "feijão"]},
        {"id": 2, "itens": ["arroz", "feijão"]},
        {"id": 3, "itens": ["arroz", "feijão"]},
        {"id": 4, "itens": ["caviar", "trufa"]},  # outlier -> score 1.0
    ]
    anomalias, threshold = detectar_anomalias(itemsets_frequentes=itemsets,
                                              transacoes=transacoes,
                                              threshold_percentil=75.0)

    ids = {a["id"] for a in anomalias}
    assert 4 in ids
    assert 0.0 <= threshold <= 1.0


def test_anomalias_ordenadas_por_score():
    itemsets = {frozenset(["a"]): 0.8}
    transacoes = [
        {"id": 1, "itens": ["a"]},
        {"id": 2, "itens": ["desconhecido"]},
        {"id": 3, "itens": ["outro_raro"]},
    ]
    anomalias, _ = detectar_anomalias(transacoes, itemsets, threshold_percentil=0.0)

    scores = [a["score_anomalia"] for a in anomalias]
    assert scores == sorted(scores, reverse=True)


# ─────────────────────────────────────────────
#  Métricas de avaliação
# ─────────────────────────────────────────────

def test_metricas_deteccao_perfeita():
    """Detecção idêntica ao ground truth -> precisão/recall/f1 = 1.0."""
    reais = [{"id": 1}, {"id": 2}]
    detectadas = [{"id": 1}, {"id": 2}]
    m = avaliar_deteccao(detectadas, reais)

    assert m["precisao"] == 1.0
    assert m["recall"] == 1.0
    assert m["f1_score"] == 1.0
    assert m["verdadeiros_positivos"] == 2
    assert m["falsos_positivos"] == 0
    assert m["falsos_negativos"] == 0


def test_metricas_com_falsos_positivos_e_negativos():
    reais = [{"id": 1}, {"id": 2}]
    detectadas = [{"id": 1}, {"id": 99}]  # acerta 1, erra 99, perde 2
    m = avaliar_deteccao(detectadas, reais)

    assert m["verdadeiros_positivos"] == 1
    assert m["falsos_positivos"] == 1
    assert m["falsos_negativos"] == 1
    assert m["precisao"] == 0.5
    assert m["recall"] == 0.5
    assert m["f1_score"] == pytest.approx(0.5, abs=1e-4)


def test_metricas_sem_deteccoes():
    """Nenhuma detecção -> métricas zeradas sem divisão por zero."""
    m = avaliar_deteccao([], [{"id": 1}])
    assert m["precisao"] == 0.0
    assert m["recall"] == 0.0
    assert m["f1_score"] == 0.0
