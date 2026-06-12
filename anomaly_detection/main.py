"""
main.py
-------
Ponto de entrada do sistema de detecção de anomalias em compras.

Sem argumentos  → menu interativo (escolha do modo de operação).
Com argumentos  → execução direta via flags (compatível com CI/scripts).

Uso:
  python main.py                        # abre o menu interativo
  python main.py --normais 300 --anomalas 30 --suporte 0.04 --confianca 0.45
"""

import argparse
import sys
import os

# Garante saída UTF-8 no terminal (Windows usa cp1252 por padrão, o que
# quebra ao imprimir os caracteres de caixa e emojis do relatório).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Garante que os módulos do pacote sejam encontrados
sys.path.insert(0, os.path.dirname(__file__))

from data_generator import gerar_dataset
from apriori import resumo_apriori
from anomaly_detector import calcular_score_anomalia, detectar_anomalias, avaliar_deteccao
from menu import ConfigExecucao, exibir_menu
from visualizer import (
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


def _config_de_args(args: argparse.Namespace) -> ConfigExecucao:
    return ConfigExecucao(
        normais=args.normais,
        anomalas=args.anomalas,
        suporte=args.suporte,
        confianca=args.confianca,
        percentil=args.percentil,
        top_regras=args.top_regras,
        graficos=args.graficos,
    )


# ─────────────────────────────────────────────
#  Pipeline de execução
# ─────────────────────────────────────────────

def executar(cfg: ConfigExecucao, titulo_extra: str = "") -> None:
    """Executa o pipeline completo para uma ConfigExecucao."""
    cabecalho = "  🛒  SISTEMA DE DETECÇÃO DE ANOMALIAS EM COMPRAS"
    if titulo_extra:
        cabecalho += f"\n       {titulo_extra}"

    print("\n" + "═" * 65)
    print(cabecalho)
    print("       Baseado no Algoritmo Apriori — Python")
    print("═" * 65)

    # ── PASSO 1: Gerar dataset ───────────────────────────────────────────────
    print(f"\n  ⏳ Gerando dataset: {cfg.normais} normais + {cfg.anomalas} anômalas...")
    dataset, anomalas_reais = gerar_dataset(
        n_normais=cfg.normais,
        n_anomalas=cfg.anomalas,
    )
    exibir_resumo_dataset(dataset)

    # ── PASSO 2: Algoritmo Apriori ───────────────────────────────────────────
    print(f"\n  ⏳ Executando Apriori (suporte ≥ {cfg.suporte:.0%}, confiança ≥ {cfg.confianca:.0%})...")
    transacoes_itens = [t["itens"] for t in dataset]
    itemsets, regras = resumo_apriori(
        transacoes_itens,
        min_support=cfg.suporte,
        min_confidence=cfg.confianca,
    )
    print(f"  ✅ {len(itemsets)} itemsets frequentes encontrados")
    print(f"  ✅ {len(regras)} regras de associação geradas")

    exibir_itemsets_frequentes(itemsets, top_n=15)
    exibir_regras(regras, top_n=cfg.top_regras)

    # ── PASSO 3: Calcular scores e detectar anomalias ────────────────────────
    print(f"\n  ⏳ Calculando scores de anomalia (percentil = {cfg.percentil:.0f}º)...")

    for t in dataset:
        t["score_anomalia"] = calcular_score_anomalia(t["itens"], itemsets)

    anomalias_detectadas, threshold = detectar_anomalias(
        dataset,
        itemsets,
        threshold_percentil=cfg.percentil,
    )

    exibir_anomalias_detectadas(anomalias_detectadas, threshold)

    # ── PASSO 4: Avaliar detecção ────────────────────────────────────────────
    metricas = avaliar_deteccao(anomalias_detectadas, anomalas_reais)
    exibir_metricas(metricas)

    # ── PASSO 5: Gráficos (opcional) ─────────────────────────────────────────
    if cfg.graficos:
        print("\n  ⏳ Gerando gráficos...")
        gerar_graficos(dataset, anomalias_detectadas, itemsets, metricas)

    print("\n" + "═" * 65)
    print("  ✅ Pipeline concluído com sucesso!")
    print("═" * 65 + "\n")


# ─────────────────────────────────────────────
#  Ponto de entrada
# ─────────────────────────────────────────────

def main() -> None:
    # Com argumentos CLI → execução direta (compatível com CI e scripts)
    if len(sys.argv) > 1:
        executar(_config_de_args(parse_args()))
        return

    # Sem argumentos → menu interativo
    configs = exibir_menu()

    if len(configs) == 1:
        executar(configs[0])
    else:
        # Modo demonstração: executa cada cenário com seu nome como título
        from menu import DEMOS
        for cfg, demo in zip(configs, DEMOS):
            input(f"\n  Pressione Enter para executar: {demo['nome']}...")
            executar(cfg, titulo_extra=f"Cenário: {demo['nome']}")
        print("  🎬 Demonstração concluída! Todos os cenários foram executados.\n")


if __name__ == "__main__":
    main()
