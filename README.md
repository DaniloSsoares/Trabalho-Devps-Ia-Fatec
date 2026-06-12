# 🛒 Detecção de Anomalias em Compras com Algoritmo Apriori

[![CI](https://github.com/DaniloSsoares/Trabalho-Devps-Ia-Fatec/actions/workflows/ci.yml/badge.svg)](https://github.com/DaniloSsoares/Trabalho-Devps-Ia-Fatec/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

Sistema em Python que usa mineração de regras de associação para identificar compras incomuns em transações de supermercado.

---

## 📚 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Executar](#-como-executar)
- [Parâmetros Disponíveis](#-parâmetros-disponíveis)
- [Exemplo de Saída](#-exemplo-de-saída)

---

## 🔍 O que é o Algoritmo Apriori?

O **Apriori** é um algoritmo clássico de **mineração de dados**, proposto por Agrawal e Srikant em 1994. Ele é utilizado para descobrir **padrões ocultos em grandes conjuntos de transações** — como um supermercado que quer saber quais produtos são frequentemente comprados juntos.

O nome "Apriori" vem do princípio fundamental que o guia:

> **Princípio Apriori:** Se um conjunto de itens é **frequente**, então **todos os seus subconjuntos também são frequentes**. E, inversamente, se um itemset é **infrequente**, nenhum de seus superconjuntos pode ser frequente.

Essa propriedade permite **podar o espaço de busca** drasticamente, tornando o algoritmo eficiente mesmo com milhares de produtos.

---

## 🔍 Sobre o Projeto

O projeto utiliza o **algoritmo Apriori** para aprender padrões de compras frequentes e, a partir disso, detectar transações que fogem do comportamento normal.

### Como funciona?

1. **Aprende o padrão normal** — O Apriori analisa o histórico de compras e descobre quais combinações de produtos são comuns (ex: arroz + feijão).
2. **Calcula um score de anomalia** — Para cada transação, verifica o quanto ela se encaixa nos padrões aprendidos. Quanto menos se encaixa, maior o score.
3. **Detecta anomalias** — Transações com score acima de um threshold (calculado automaticamente por percentil) são marcadas como anômalas.

```
  Dataset de Compras
         │
         ▼
  ┌─────────────┐      ┌──────────────────────┐
  │   Apriori   │─────►│ Padrões Frequentes   │
  └─────────────┘      └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Score de Anomalia   │
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
             Score baixo                   Score alto
             ✅ NORMAL                     🚨 ANOMALIA
```

---

## 📁 Estrutura do Projeto

```
anomaly_detection/
├── main.py               # Ponto de entrada — executa o pipeline completo
├── data_generator.py     # Gera transações sintéticas (normais + anômalas)
├── apriori.py            # Implementação do algoritmo Apriori
├── anomaly_detector.py   # Cálculo de scores e detecção de anomalias
├── visualizer.py         # Relatórios no terminal + gráficos PNG
├── __init__.py           # Definição do pacote Python
└── requirements.txt      # Dependências (matplotlib)
```

---

## ▶️ Como Executar

### Pré-requisitos

- Python 3.8+
- `matplotlib` (opcional, apenas para gráficos)

```bash
# Instalar dependências (opcional)
pip install matplotlib
```

### Rodar o sistema

```bash
cd anomaly_detection

# Configurações padrão
python3 main.py

# Com gráficos PNG
python3 main.py --graficos

# Personalizando parâmetros
python3 main.py --normais 300 --anomalas 30 --suporte 0.04 --confianca 0.45 --percentil 92
```

---

## 🧪 Testes

O projeto possui uma suíte de testes automatizados (`pytest`) que roda no CI a cada push e pull request.

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar os testes
python -m pytest -v
```

---

## 🎛️ Parâmetros Disponíveis

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--normais` | `200` | Nº de transações normais |
| `--anomalas` | `20` | Nº de transações anômalas |
| `--suporte` | `0.05` | Suporte mínimo do Apriori |
| `--confianca` | `0.40` | Confiança mínima para regras |
| `--percentil` | `90.0` | Percentil de corte para anomalias |
| `--top-regras` | `10` | Nº de regras exibidas no relatório |
| `--graficos` | `False` | Gerar gráficos PNG (requer matplotlib) |

---

## 📊 Exemplo de Saída

```
═══════════════════════════════════════════════════════════════
  🛒  SISTEMA DE DETECÇÃO DE ANOMALIAS EM COMPRAS
═══════════════════════════════════════════════════════════════

  📊 RESUMO DO DATASET
  Total de transações : 220
  ✅ Normais          : 200 (90.9%)
  🚨 Anômalas (reais) : 20  (9.1%)

  📊 TOP ITEMSETS FREQUENTES
  {arroz}                    25.00%  ███████░░░░
  {feijão}                   20.91%  ██████░░░░░
  {arroz, feijão}            20.45%  ██████░░░░░

  📊 ANOMALIAS DETECTADAS
   ID    Score  Itens
    42   1.000  🚨 caviar, filé_mignon, salmão...

  📊 MÉTRICAS DE AVALIAÇÃO
  Precisão  : 85.00%
  Recall    : 80.00%
  F1-Score  : 82.35%
```

---

## 📖 Referências

- Agrawal, R., & Srikant, R. (1994). *Fast Algorithms for Mining Association Rules*. VLDB Conference.
- Han, J., Kamber, M., & Pei, J. (2011). *Data Mining: Concepts and Techniques*. Morgan Kaufmann.
