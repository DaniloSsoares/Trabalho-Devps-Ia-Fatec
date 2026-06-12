"""
menu.py
-------
Menu interativo para escolha do modo de operação do sistema.
Ativado automaticamente quando main.py é executado sem argumentos CLI.
"""

import sys
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────
#  Configuração de execução
# ─────────────────────────────────────────────

@dataclass
class ConfigExecucao:
    normais: int     = 200
    anomalas: int    = 20
    suporte: float   = 0.05
    confianca: float = 0.40
    percentil: float = 90.0
    top_regras: int  = 10
    graficos: bool   = False


# Presets para o modo Demonstração
DEMOS = [
    {
        "nome": "Dataset Pequeno",
        "desc": "50 transações normais + 5 anômalas — execução rápida para entender o fluxo",
        "config": ConfigExecucao(normais=50, anomalas=5, suporte=0.08, confianca=0.40, percentil=85.0),
    },
    {
        "nome": "Dataset Padrão",
        "desc": "200 normais + 20 anômalas — configuração balanceada (mesmos defaults)",
        "config": ConfigExecucao(normais=200, anomalas=20, suporte=0.05, confianca=0.40, percentil=90.0),
    },
    {
        "nome": "Detector Agressivo",
        "desc": "300 normais + 30 anômalas — threshold alto (95º percentil), captura mais anomalias",
        "config": ConfigExecucao(normais=300, anomalas=30, suporte=0.04, confianca=0.35, percentil=95.0),
    },
]


# ─────────────────────────────────────────────
#  Helpers de I/O
# ─────────────────────────────────────────────

def _linha(char: str = "─", largura: int = 65) -> str:
    return char * largura


def _cabecalho_menu() -> None:
    print("\n" + _linha("═"))
    print("  🛒  SISTEMA DE DETECÇÃO DE ANOMALIAS EM COMPRAS")
    print("       Baseado no Algoritmo Apriori — Python")
    print(_linha("═"))


def _ler_int(prompt: str, minimo: int, maximo: int, padrao: int) -> int:
    while True:
        entrada = input(f"  {prompt} [{padrao}]: ").strip()
        if entrada == "":
            return padrao
        try:
            valor = int(entrada)
            if minimo <= valor <= maximo:
                return valor
            print(f"  ⚠  Digite um valor entre {minimo} e {maximo}.")
        except ValueError:
            print("  ⚠  Valor inválido. Digite um número inteiro.")


def _ler_float(prompt: str, minimo: float, maximo: float, padrao: float) -> float:
    while True:
        entrada = input(f"  {prompt} [{padrao}]: ").strip()
        if entrada == "":
            return padrao
        try:
            valor = float(entrada)
            if minimo <= valor <= maximo:
                return valor
            print(f"  ⚠  Digite um valor entre {minimo} e {maximo}.")
        except ValueError:
            print("  ⚠  Valor inválido. Digite um número decimal.")


def _ler_opcao(opcoes: list[str]) -> str:
    """Lê uma opção válida da lista, sem distinção de maiúsculas."""
    while True:
        entrada = input("  Escolha: ").strip().lower()
        if entrada in [o.lower() for o in opcoes]:
            return entrada
        print(f"  ⚠  Opção inválida. Escolha entre: {', '.join(opcoes)}")


# ─────────────────────────────────────────────
#  Modos de operação
# ─────────────────────────────────────────────

def _modo_rapido() -> ConfigExecucao:
    print("\n" + _linha())
    print("  ⚡ MODO RÁPIDO")
    print(_linha())
    print("  Usando configurações padrão.")
    print(f"  • Transações normais  : 200")
    print(f"  • Transações anômalas : 20")
    print(f"  • Suporte mínimo      : 5%")
    print(f"  • Confiança mínima    : 40%")
    print(f"  • Percentil threshold : 90º")
    return ConfigExecucao()


def _modo_personalizado() -> ConfigExecucao:
    print("\n" + _linha())
    print("  🎛️  MODO PERSONALIZADO")
    print(_linha())
    print("  Configure os parâmetros abaixo. Pressione Enter para manter o padrão.\n")

    normais   = _ler_int("Nº de transações normais   (10–2000)", 10, 2000, 200)
    anomalas  = _ler_int("Nº de transações anômalas  (1–500)",   1,  500,  20)
    suporte   = _ler_float("Suporte mínimo Apriori     (0.01–0.50)", 0.01, 0.50, 0.05)
    confianca = _ler_float("Confiança mínima Apriori   (0.10–0.99)", 0.10, 0.99, 0.40)
    percentil = _ler_float("Percentil de corte         (50–99)",     50.0, 99.0, 90.0)
    top_reg   = _ler_int("Nº de regras a exibir      (5–50)",     5,   50,   10)

    print("\n  Gerar gráficos PNG? (requer matplotlib)")
    graficos = _ler_opcao(["s", "n"]) == "s"

    print("\n" + _linha())
    print("  📋 Configuração definida:")
    print(f"  • Normais / Anômalas  : {normais} / {anomalas}")
    print(f"  • Suporte / Confiança : {suporte:.0%} / {confianca:.0%}")
    print(f"  • Percentil           : {percentil:.0f}º")
    print(f"  • Top regras          : {top_reg}")
    print(f"  • Gráficos            : {'Sim' if graficos else 'Não'}")

    return ConfigExecucao(
        normais=normais, anomalas=anomalas,
        suporte=suporte, confianca=confianca,
        percentil=percentil, top_regras=top_reg,
        graficos=graficos,
    )


def _modo_demonstracao() -> list[ConfigExecucao]:
    print("\n" + _linha())
    print("  🎬 MODO DEMONSTRAÇÃO")
    print(_linha())
    print("  Executa 3 cenários em sequência para comparar resultados:\n")

    for i, demo in enumerate(DEMOS, 1):
        c = demo["config"]
        print(f"  {i}. {demo['nome']}")
        print(f"     {demo['desc']}")
        print(f"     Normais={c.normais} | Anômalas={c.anomalas} | "
              f"Suporte={c.suporte:.0%} | Percentil={c.percentil:.0f}º\n")

    print("  Todos os cenários serão executados automaticamente.")
    return [d["config"] for d in DEMOS]


# ─────────────────────────────────────────────
#  Ponto de entrada do menu
# ─────────────────────────────────────────────

def exibir_menu() -> list[ConfigExecucao]:
    """
    Exibe o menu principal e retorna uma lista de ConfigExecucao.
    Em modo rápido ou personalizado retorna lista de 1 item.
    Em modo demonstração retorna lista de 3 itens (um por cenário).
    """
    _cabecalho_menu()

    print("\n  Escolha o modo de operação:\n")
    print("  [1] ⚡ Rápido          — executa com configurações padrão")
    print("  [2] 🎛️  Personalizado   — você define cada parâmetro")
    print("  [3] 🎬 Demonstração    — 3 cenários comparativos automáticos")
    print("  [0] 🚪 Sair\n")

    escolha = _ler_opcao(["1", "2", "3", "0"])

    if escolha == "0":
        print("\n  Até logo!\n")
        sys.exit(0)

    if escolha == "1":
        return [_modo_rapido()]

    if escolha == "2":
        return [_modo_personalizado()]

    return _modo_demonstracao()
