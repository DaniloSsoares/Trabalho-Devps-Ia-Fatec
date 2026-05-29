"""
main.py
-------
Ponto de entrada do sistema de detecção de anomalias em compras.

Fluxo completo:
  1. Gerar dataset sintético de transações
  2. Executar o algoritmo Apriori → itemsets e regras
  3. Calcular scores de anomalia para cada transação
  4. Detectar anomalias por threshold de percentil
  5. Avaliar com métricas e exibir resultados
  6. Gerar gráficos (requer matplotlib)

Uso:
  python main.py                        # padrão
  python main.py --normais 300 --anomalas 30 --suporte 0.04 --confianca 0.45
"""

import argparse
import sys
import os

# Garante que os módulos do pacote sejam encontrados
sys.path.insert(0, os.path.dirname(__file__))

from data_generator import gerar_dataset
from apriori import resumo_apriori
from anomaly_detector import calcular_score_anomalia, detectar_anomalias, avaliar_deteccao
from visualizer import (
    exibir_cabecalho,
    exibir_resumo_dataset,
    exibir_itemsets_frequentes,
    exibir_regras,
    exibir_anomalias_detectadas,
    exibir_metricas,
    gerar_graficos,
)


# ─────────────────────────────────────────────
#  Argumentos de linha de comando
# ─────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sistema de Detecção de Anomalias em Compras via Apriori",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--normais",    type=int,   default=200,  help="Nº de transações normais (default: 200)")
    parser.add_argument("--anomalas",   type=int,   default=20,   help="Nº de transações anômalas (default: 20)")
    parser.add_argument("--suporte",    type=float, default=0.05, help="Suporte mínimo Apriori (default: 0.05)")
    parser.add_argument("--confianca",  type=float, default=0.40, help="Confiança mínima Apriori (default: 0.40)")
    parser.add_argument("--percentil",  type=float, default=90.0, help="Percentil para threshold de anomalia (default: 90)")
    parser.add_argument("--graficos",   action="store_true",      help="Gerar e salvar gráficos PNG")
    parser.add_argument("--top-regras", type=int,   default=10,   help="Nº de regras a exibir (default: 10)")
    return parser.parse_args()


# ─────────────────────────────────────────────
#  Pipeline principal
# ─────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    print("\n" + "═" * 65)
    print("  🛒  SISTEMA DE DETECÇÃO DE ANOMALIAS EM COMPRAS")
    print("       Baseado no Algoritmo Apriori — Python")
    print("═" * 65)

    # ── PASSO 1: Gerar dataset ───────────────────────────────────────────────
    print(f"\n  ⏳ Gerando dataset: {args.normais} normais + {args.anomalas} anômalas...")
    dataset, anomalas_reais = gerar_dataset(
        n_normais=args.normais,
        n_anomalas=args.anomalas,
    )
    exibir_resumo_dataset(dataset)

    # ── PASSO 2: Algoritmo Apriori ───────────────────────────────────────────
    print(f"\n  ⏳ Executando Apriori (suporte ≥ {args.suporte:.0%}, confiança ≥ {args.confianca:.0%})...")
    transacoes_itens = [t["itens"] for t in dataset]
    itemsets, regras = resumo_apriori(
        transacoes_itens,
        min_support=args.suporte,
        min_confidence=args.confianca,
    )
    print(f"  ✅ {len(itemsets)} itemsets frequentes encontrados")
    print(f"  ✅ {len(regras)} regras de associação geradas")

    exibir_itemsets_frequentes(itemsets, top_n=15)
    exibir_regras(regras, top_n=args.top_regras)

    # ── PASSO 3: Calcular scores e detectar anomalias ────────────────────────
    print(f"\n  ⏳ Calculando scores de anomalia (percentil = {args.percentil:.0f}º)...")

    # Enriquece o dataset com scores antes de detectar
    for t in dataset:
        t["score_anomalia"] = calcular_score_anomalia(t["itens"], itemsets)

    anomalias_detectadas, threshold = detectar_anomalias(
        dataset,
        itemsets,
        threshold_percentil=args.percentil,
    )

    exibir_anomalias_detectadas(anomalias_detectadas, threshold)

    # ── PASSO 4: Avaliar detecção ────────────────────────────────────────────
    metricas = avaliar_deteccao(anomalias_detectadas, anomalas_reais)
    exibir_metricas(metricas)

    # ── PASSO 5: Gráficos (opcional) ─────────────────────────────────────────
    if args.graficos:
        print("\n  ⏳ Gerando gráficos...")
        gerar_graficos(dataset, anomalias_detectadas, itemsets, metricas)

    print("\n" + "═" * 65)
    print("  ✅ Pipeline concluído com sucesso!")
    print("═" * 65 + "\n")


if __name__ == "__main__":
    main()
