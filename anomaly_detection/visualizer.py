"""
visualizer.py
-------------
Módulo de visualização dos resultados do sistema de detecção de anomalias.
Gera relatórios em texto no terminal e salva gráficos em PNG.
"""

import os
from typing import Dict, FrozenSet, List

# ─────────────────────────────────────────────
#  Utilitários de formatação
# ─────────────────────────────────────────────

def _barra(valor: float, largura: int = 30, char: str = "█") -> str:
    """Retorna uma barra de progresso proporcional ao valor (0.0 a 1.0)."""
    preenchido = int(valor * largura)
    return char * preenchido + "░" * (largura - preenchido)


def _formatar_itemset(itemset: FrozenSet[str]) -> str:
    return "{" + ", ".join(sorted(itemset)) + "}"


# ─────────────────────────────────────────────
#  Relatórios em texto
# ─────────────────────────────────────────────

def exibir_cabecalho(titulo: str) -> None:
    linha = "═" * 65
    print(f"\n{linha}")
    print(f"  {'📊 ' + titulo}")
    print(linha)


def exibir_resumo_dataset(transacoes: List[dict]) -> None:
    exibir_cabecalho("RESUMO DO DATASET")

    normais = sum(1 for t in transacoes if t.get("label") == "normal")
    anomalas = sum(1 for t in transacoes if t.get("label") == "anomalia")
    total = len(transacoes)

    print(f"  Total de transações : {total}")
    print(f"  ✅ Normais          : {normais} ({normais/total*100:.1f}%)")
    print(f"  🚨 Anômalas (reais) : {anomalas} ({anomalas/total*100:.1f}%)")

    tamanhos = [len(t["itens"]) for t in transacoes]
    print(f"  Tamanho médio       : {sum(tamanhos)/len(tamanhos):.2f} itens")
    print(f"  Tamanho máx/mín     : {max(tamanhos)} / {min(tamanhos)} itens")


def exibir_itemsets_frequentes(
    itemsets: Dict[FrozenSet[str], float],
    top_n: int = 15,
) -> None:
    exibir_cabecalho(f"TOP {top_n} ITEMSETS FREQUENTES (Apriori)")

    ordenados = sorted(itemsets.items(), key=lambda x: x[1], reverse=True)[:top_n]

    print(f"  {'Itemset':<45} {'Suporte':>8}  {'Barra'}")
    print(f"  {'─'*45} {'─'*8}  {'─'*30}")

    for itemset, suporte in ordenados:
        label = _formatar_itemset(itemset)
        if len(label) > 44:
            label = label[:41] + "..."
        barra = _barra(suporte)
        print(f"  {label:<45} {suporte:>7.2%}  {barra}")


def exibir_regras(regras, top_n: int = 10) -> None:
    exibir_cabecalho(f"TOP {top_n} REGRAS DE ASSOCIAÇÃO (por Lift)")

    print(f"  {'Antecedente → Consequente':<52} {'Sup':>6} {'Conf':>6} {'Lift':>6}")
    print(f"  {'─'*52} {'─'*6} {'─'*6} {'─'*6}")

    for r in regras[:top_n]:
        ant = _formatar_itemset(r.antecedente)
        con = _formatar_itemset(r.consequente)
        regra = f"{ant} → {con}"
        if len(regra) > 51:
            regra = regra[:48] + "..."
        print(f"  {regra:<52} {r.suporte:>5.2%} {r.confianca:>5.2%} {r.lift:>6.2f}")


def exibir_anomalias_detectadas(
    anomalias: List[dict],
    threshold: float,
    top_n: int = 15,
) -> None:
    exibir_cabecalho(f"ANOMALIAS DETECTADAS (threshold = {threshold:.4f})")

    print(f"  Total detectadas: {len(anomalias)}\n")
    print(f"  {'ID':>4}  {'Score':>7}  {'Barra':<25}  {'Itens'}")
    print(f"  {'─'*4}  {'─'*7}  {'─'*25}  {'─'*35}")

    for t in anomalias[:top_n]:
        score = t["score_anomalia"]
        itens = ", ".join(sorted(t["itens"]))
        if len(itens) > 45:
            itens = itens[:42] + "..."
        icone = "🚨" if t.get("label") == "anomalia" else "⚠️ "
        barra = _barra(score, largura=20, char="▓")
        print(f"  {t['id']:>4}  {score:>7.4f}  {barra:<25}  {icone} {itens}")

        if t.get("motivo"):
            print(f"         ↳ Motivo: {t['motivo']}")


def exibir_metricas(metricas: dict) -> None:
    exibir_cabecalho("MÉTRICAS DE AVALIAÇÃO")

    vp = metricas["verdadeiros_positivos"]
    fp = metricas["falsos_positivos"]
    fn = metricas["falsos_negativos"]

    print(f"  ✅ Verdadeiros Positivos : {vp}")
    print(f"  ❌ Falsos Positivos      : {fp}")
    print(f"  ⭕ Falsos Negativos      : {fn}")
    print()
    print(f"  Precisão  : {metricas['precisao']:.2%}  {_barra(metricas['precisao'])}")
    print(f"  Recall    : {metricas['recall']:.2%}  {_barra(metricas['recall'])}")
    print(f"  F1-Score  : {metricas['f1_score']:.2%}  {_barra(metricas['f1_score'])}")


# ─────────────────────────────────────────────
#  Gráficos com matplotlib (opcional)
# ─────────────────────────────────────────────

def gerar_graficos(
    transacoes: List[dict],
    anomalias: List[dict],
    itemsets: Dict[FrozenSet[str], float],
    metricas: dict,
    salvar_em: str = "./graficos",
) -> None:
    """Gera e salva gráficos de análise. Requer matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("\n  matplotlib não encontrado. Instale com: pip install matplotlib")
        return

    os.makedirs(salvar_em, exist_ok=True)

    # ── Gráfico 1: Distribuição dos scores ──────────────────────────────────
    scores_normais = [t["score_anomalia"] for t in transacoes
                      if t.get("label") == "normal" and "score_anomalia" in t]
    scores_anomalas = [t["score_anomalia"] for t in transacoes
                       if t.get("label") == "anomalia" and "score_anomalia" in t]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor("#0f0f1a")

    ax1 = axes[0]
    ax1.set_facecolor("#1a1a2e")
    if scores_normais:
        ax1.hist(scores_normais, bins=20, color="#4cc9f0", alpha=0.7, label="Normal", edgecolor="white")
    if scores_anomalas:
        ax1.hist(scores_anomalas, bins=10, color="#f72585", alpha=0.8, label="Anômala", edgecolor="white")
    ax1.set_title("Distribuição dos Scores de Anomalia", color="white", fontsize=13, pad=12)
    ax1.set_xlabel("Score de Anomalia", color="#aaaacc")
    ax1.set_ylabel("Frequência", color="#aaaacc")
    ax1.tick_params(colors="white")
    ax1.spines[:].set_color("#333355")
    ax1.legend(facecolor="#1a1a2e", labelcolor="white")

    # ── Gráfico 2: Top 10 itemsets por suporte ───────────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor("#1a1a2e")

    top10 = sorted(itemsets.items(), key=lambda x: x[1], reverse=True)[:10]
    labels = [", ".join(sorted(k))[:28] for k, _ in top10]
    valores = [v for _, v in top10]

    bars = ax2.barh(labels[::-1], valores[::-1],
                    color=["#7209b7", "#560bad", "#480ca8",
                           "#3a0ca3", "#3f37c9", "#4361ee",
                           "#4895ef", "#4cc9f0", "#06d6a0", "#f72585"][:len(labels)],
                    edgecolor="none")
    ax2.set_title("Top 10 Itemsets Frequentes", color="white", fontsize=13, pad=12)
    ax2.set_xlabel("Suporte", color="#aaaacc")
    ax2.tick_params(colors="white", labelsize=8)
    ax2.spines[:].set_color("#333355")

    for bar, val in zip(bars, valores[::-1]):
        ax2.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1%}", va="center", color="white", fontsize=8)

    plt.tight_layout(pad=2)
    caminho1 = os.path.join(salvar_em, "analise_anomalias.png")
    plt.savefig(caminho1, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"\n  Gráfico salvo em: {caminho1}")

    # ── Gráfico 3: Métricas de avaliação ────────────────────────────────────
    fig2, ax3 = plt.subplots(figsize=(6, 4))
    fig2.patch.set_facecolor("#0f0f1a")
    ax3.set_facecolor("#1a1a2e")

    nomes = ["Precisão", "Recall", "F1-Score"]
    vals = [metricas["precisao"], metricas["recall"], metricas["f1_score"]]
    cores = ["#4cc9f0", "#06d6a0", "#f72585"]

    barras = ax3.bar(nomes, vals, color=cores, edgecolor="none", width=0.5)
    ax3.set_ylim(0, 1.15)
    ax3.set_title("Métricas de Avaliação do Detector", color="white", fontsize=13, pad=12)
    ax3.tick_params(colors="white")
    ax3.spines[:].set_color("#333355")

    for b, v in zip(barras, vals):
        ax3.text(b.get_x() + b.get_width() / 2, v + 0.03,
                 f"{v:.0%}", ha="center", color="white", fontsize=12, fontweight="bold")

    caminho2 = os.path.join(salvar_em, "metricas_avaliacao.png")
    plt.savefig(caminho2, dpi=120, bbox_inches="tight", facecolor=fig2.get_facecolor())
    plt.close()
    print(f"  Gráfico salvo em: {caminho2}")
