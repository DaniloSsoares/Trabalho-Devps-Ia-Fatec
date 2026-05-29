"""
data_generator.py
-----------------
Módulo responsável por gerar transações sintéticas de compras.
Inclui transações "normais" (padrões frequentes) e transações "anômalas"
(itens raramente comprados juntos ou combinações suspeitas).
"""

import random
from typing import List, Tuple

# Seed para reprodutibilidade
random.seed(42)

# Catálogo de produtos por categoria
PRODUTOS = {
    "mercearia":    ["arroz", "feijão", "macarrão", "farinha", "açúcar", "sal", "óleo"],
    "laticínios":   ["leite", "queijo", "manteiga", "iogurte", "requeijão"],
    "hortifruti":   ["banana", "maçã", "alface", "tomate", "cebola", "batata"],
    "bebidas":      ["suco", "refrigerante", "água", "cerveja", "vinho"],
    "higiene":      ["sabonete", "shampoo", "condicionador", "pasta_de_dente", "desodorante"],
    "limpeza":      ["detergente", "sabão_em_pó", "amaciante", "desinfetante"],
    "padaria":      ["pão_francês", "pão_de_forma", "biscoito", "bolo"],
    "frios":        ["presunto", "salame", "mortadela", "peito_de_peru"],
    "congelados":   ["pizza_congelada", "nuggets", "lasanha_congelada", "hambúrguer"],
    "luxo":         ["vinho_importado", "salmão", "filé_mignon", "trufa", "caviar"],
}

# Padrões frequentes (compras normais e esperadas)
# IMPORTANTE: não incluem itens de luxo para garantir separabilidade
PADROES_NORMAIS: List[List[str]] = [
    ["arroz", "feijão", "óleo"],
    ["arroz", "feijão", "sal", "óleo"],
    ["arroz", "feijão", "sal"],
    ["pão_francês", "manteiga", "leite"],
    ["pão_de_forma", "presunto", "queijo"],
    ["pão_francês", "manteiga"],
    ["leite", "açúcar", "farinha"],
    ["leite", "iogurte", "queijo"],
    ["detergente", "sabão_em_pó", "amaciante"],
    ["detergente", "desinfetante"],
    ["sabonete", "shampoo", "condicionador"],
    ["pasta_de_dente", "sabonete", "desodorante"],
    ["shampoo", "condicionador", "sabonete"],
    ["banana", "maçã", "leite", "iogurte"],
    ["banana", "maçã", "laranja"],
    ["tomate", "alface", "cebola"],
    ["tomate", "cebola", "batata"],
    ["arroz", "feijão", "alface", "tomate"],
    ["refrigerante", "biscoito"],
    ["pizza_congelada", "refrigerante"],
    ["nuggets", "hambúrguer", "refrigerante"],
    ["arroz", "macarrão", "molho_de_tomate"],
    ["macarrão", "molho_de_tomate"],
    ["presunto", "queijo", "pão_de_forma"],
    ["mortadela", "pão_de_forma"],
]

# Padrões anômalos (compras suspeitas ou incomuns)
# Contêm itens de luxo/raros que NUNCA aparecem nos padrões normais
PADROES_ANOMALOS: List[Tuple[List[str], str]] = [
    # (itens, motivo da anomalia)
    (["vinho_importado", "caviar", "trufa", "filé_mignon", "salmão"],
     "Compra de luxo em horário incomum"),
    (["vinho_importado", "caviar", "trufa"],
     "Apenas itens de luxo — perfil atípico"),
    (["filé_mignon", "salmão", "caviar"],
     "Compra de carnes premium sem itens básicos"),
    (["trufa", "filé_mignon", "vinho_importado", "salmão"],
     "Cesta de luxo completa — cliente VIP ou fraude"),
    (["caviar", "trufa", "vinho_importado"],
     "Apenas itens de altíssimo valor"),
    (["filé_mignon", "caviar", "vinho_importado"],
     "Combinação de itens premium sem padrão normal"),
    (["salmão", "trufa", "caviar"],
     "Frutos do mar e condimentos de luxo"),
    (["vinho_importado", "filé_mignon", "trufa", "caviar", "salmão"],
     "Cesta premium completa — padrão atípico máximo"),
    (["vinho_importado", "salmão", "trufa"],
     "Combinação rara de itens premium"),
    (["caviar", "filé_mignon", "trufa"],
     "Produtos exclusivos sem contexto normal"),
]


def gerar_transacao_normal() -> List[str]:
    """Gera uma transação normal baseada nos padrões frequentes com pequenas variações."""
    padrao = random.choice(PADROES_NORMAIS)
    transacao = list(padrao)

    # Adiciona 0 a 2 itens extras aleatórios com baixa probabilidade
    if random.random() < 0.3:
        categoria = random.choice(list(PRODUTOS.keys()))
        item_extra = random.choice(PRODUTOS[categoria])
        if item_extra not in transacao:
            transacao.append(item_extra)

    return transacao


def gerar_transacao_anomala() -> Tuple[List[str], str]:
    """Gera uma transação anômala aleatória com seu motivo."""
    return random.choice(PADROES_ANOMALOS)


def gerar_dataset(
    n_normais: int = 200,
    n_anomalas: int = 20,
    embaralhar: bool = True,
) -> Tuple[List[dict], List[dict]]:
    """
    Gera o dataset completo de transações.

    Args:
        n_normais: Número de transações normais.
        n_anomalas: Número de transações anômalas.
        embaralhar: Se True, embaralha todas as transações.

    Returns:
        (todas_transacoes, transacoes_anomalas_reais)
        Cada transação é um dict com: id, itens, label, motivo (se anômala).
    """
    todas: List[dict] = []

    # Gera transações normais
    for i in range(n_normais):
        itens = gerar_transacao_normal()
        todas.append({
            "id": i + 1,
            "itens": itens,
            "label": "normal",
            "motivo": None,
        })

    # Gera transações anômalas
    anomalas_reais: List[dict] = []
    for j in range(n_anomalas):
        itens, motivo = gerar_transacao_anomala()
        t = {
            "id": n_normais + j + 1,
            "itens": itens,
            "label": "anomalia",
            "motivo": motivo,
        }
        todas.append(t)
        anomalas_reais.append(t)

    if embaralhar:
        random.shuffle(todas)

    return todas, anomalas_reais
