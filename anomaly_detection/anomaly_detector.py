"""
anomaly_detector.py
-------------------
Detecta transações anômalas comparando-as com os padrões
aprendidos pelo algoritmo Apriori.

Estratégia:
  - Uma transação é ANÔMALA se:
    1. Nenhum de seus itens pertence a itemsets frequentes de tamanho >= 2, OU
    2. Sua pontuação de "raridade" ultrapassa o threshold calculado
       a partir da distribuição do dataset inteiro.

  Pontuação de anomalia de uma transação T:
    score(T) = 1 - avg( suporte(itemset) para todo itemset ⊆ T presente em frequentes )
    → Quanto menor o suporte médio dos subconjuntos, mais anômala.
    → Transações com subconjuntos completamente ausentes recebem score 1.0 (máximo).
"""

from itertools import combinations
from typing import Dict, FrozenSet, List, Tuple

from apriori import Itemset


# ─────────────────────────────────────────────
#  Cálculo de pontuação de anomalia
# ─────────────────────────────────────────────

def calcular_score_anomalia(
    itens: List[str],
    itemsets_frequentes: Dict[Itemset, float],
) -> float:
    """
    Calcula o score de anomalia de uma transação (0.0 = normal, 1.0 = anômala).

    O score é baseado no suporte médio de todos os subconjuntos da transação
    que aparecem nos itemsets frequentes.
    """
    itens_unicos = list(set(itens))

    suportes_encontrados: List[float] = []

    # Avalia subconjuntos de tamanho 1 a len(itens)
    for tamanho in range(1, len(itens_unicos) + 1):
        for combo in combinations(itens_unicos, tamanho):
            itemset = frozenset(combo)
            if itemset in itemsets_frequentes:
                suportes_encontrados.append(itemsets_frequentes[itemset])

    if not suportes_encontrados:
        return 1.0  # Nenhum padrão reconhecido → score máximo de anomalia

    suporte_medio = sum(suportes_encontrados) / len(suportes_encontrados)
    return round(1.0 - suporte_medio, 6)


# ─────────────────────────────────────────────
#  Detecção de anomalias no dataset
# ─────────────────────────────────────────────

def detectar_anomalias(
    transacoes: List[dict],
    itemsets_frequentes: Dict[Itemset, float],
    threshold_percentil: float = 90.0,
) -> Tuple[List[dict], float]:
    """
    Detecta anomalias no dataset com base nos scores calculados.

    Args:
        transacoes: Lista de dicts com campos 'id' e 'itens'.
        itemsets_frequentes: Saída do módulo apriori.
        threshold_percentil: Percentil acima do qual uma transação é anômala.

    Returns:
        (anomalias_detectadas, threshold_usado)
        Cada anomalia é um dict com: id, itens, score, label, motivo.
    """
    # Calcula scores para todas as transações
    scores: List[Tuple[dict, float]] = []
    for t in transacoes:
        score = calcular_score_anomalia(t["itens"], itemsets_frequentes)
        scores.append((t, score))

    # Define o threshold como um percentil dos scores
    valores = sorted([s for _, s in scores])
    indice_threshold = int(len(valores) * threshold_percentil / 100)
    threshold = valores[min(indice_threshold, len(valores) - 1)]

    # Filtra anomalias
    anomalias: List[dict] = []
    for t, score in scores:
        t_enriquecido = {**t, "score_anomalia": score}
        if score >= threshold:
            anomalias.append(t_enriquecido)

    anomalias.sort(key=lambda x: x["score_anomalia"], reverse=True)
    return anomalias, threshold


def avaliar_deteccao(
    anomalias_detectadas: List[dict],
    anomalias_reais: List[dict],
) -> dict:
    """
    Avalia a qualidade da detecção comparando com o ground truth.

    Returns:
        Dict com métricas: verdadeiros_positivos, falsos_positivos,
        falsos_negativos, precisao, recall, f1.
    """
    ids_detectadas = {t["id"] for t in anomalias_detectadas}
    ids_reais = {t["id"] for t in anomalias_reais}

    vp = len(ids_detectadas & ids_reais)       # Verdadeiros Positivos
    fp = len(ids_detectadas - ids_reais)        # Falsos Positivos
    fn = len(ids_reais - ids_detectadas)        # Falsos Negativos

    precisao = vp / (vp + fp) if (vp + fp) > 0 else 0.0
    recall   = vp / (vp + fn) if (vp + fn) > 0 else 0.0
    f1       = (2 * precisao * recall / (precisao + recall)
                if (precisao + recall) > 0 else 0.0)

    return {
        "verdadeiros_positivos": vp,
        "falsos_positivos": fp,
        "falsos_negativos": fn,
        "precisao": round(precisao, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
    }
