# 🛒 Detecção de Anomalias em Compras com Algoritmo Apriori

> Sistema em Python que aplica mineração de regras de associação para identificar padrões incomuns em transações de compras.

---

## 📚 Sumário

- [O que é o Algoritmo Apriori?](#-o-que-é-o-algoritmo-apriori)
- [Conceitos Fundamentais](#-conceitos-fundamentais)
- [Como o Apriori Funciona](#-como-o-apriori-funciona-passo-a-passo)
- [Como foi Aplicado neste Projeto](#-como-foi-aplicado-neste-projeto)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Executar](#-como-executar)
- [Exemplo de Saída](#-exemplo-de-saída)
- [Parâmetros Disponíveis](#-parâmetros-disponíveis)

---

## 🔍 O que é o Algoritmo Apriori?

O **Apriori** é um algoritmo clássico de **mineração de dados**, proposto por Agrawal e Srikant em 1994. Ele é utilizado para descobrir **padrões ocultos em grandes conjuntos de transações** — como um supermercado que quer saber quais produtos são frequentemente comprados juntos.

O nome "Apriori" vem do princípio fundamental que o guia:

> **Princípio Apriori:** Se um conjunto de itens é **frequente**, então **todos os seus subconjuntos também são frequentes**. E, inversamente, se um itemset é **infrequente**, nenhum de seus superconjuntos pode ser frequente.

Essa propriedade permite **podar o espaço de busca** drasticamente, tornando o algoritmo eficiente mesmo com milhares de produtos.

---

## 📐 Conceitos Fundamentais

### Transação
Uma **transação** é uma compra individual. Cada transação contém um conjunto de itens adquiridos juntos.

```
Transação #001 → { arroz, feijão, óleo, sal }
Transação #002 → { pão, manteiga, leite }
Transação #003 → { shampoo, condicionador, sabonete }
```

### Itemset
Um **itemset** é qualquer subconjunto de itens. Pode ter 1, 2, 3 ou mais elementos.

```
{ arroz }              → itemset de tamanho 1
{ arroz, feijão }      → itemset de tamanho 2
{ arroz, feijão, óleo} → itemset de tamanho 3
```

### Suporte (Support)
O **suporte** mede a frequência com que um itemset aparece no dataset.

```
                    Nº de transações que contêm o itemset
Suporte(X) =  ─────────────────────────────────────────────
                        Total de transações
```

> Exemplo: Se `{arroz, feijão}` aparece em 50 de 200 transações:
> `Suporte = 50/200 = 0.25 = 25%`

### Confiança (Confidence)
A **confiança** de uma regra `A → B` mede a probabilidade de que uma transação que contém `A` também contenha `B`.

```
                    Suporte(A ∪ B)
Confiança(A → B) = ────────────────
                      Suporte(A)
```

> Exemplo: `{arroz} → {feijão}` com confiança de 80% significa que, em 80% das vezes que alguém compra arroz, também compra feijão.

### Lift
O **lift** indica se a associação entre `A` e `B` é genuína ou apenas coincidência estatística.

```
                  Confiança(A → B)
Lift(A → B) = ────────────────────────
                    Suporte(B)
```

| Lift | Interpretação |
|------|--------------|
| `> 1` | A presença de A **aumenta** a probabilidade de B (associação positiva) |
| `= 1` | A e B são **independentes** (sem associação real) |
| `< 1` | A presença de A **reduz** a probabilidade de B (associação negativa) |

---

## ⚙️ Como o Apriori Funciona (Passo a Passo)

```
┌─────────────────────────────────────────────────────────────┐
│                   DATASET DE TRANSAÇÕES                      │
│  T1: {arroz, feijão, óleo}                                  │
│  T2: {arroz, feijão, sal, óleo}                             │
│  T3: {pão, manteiga, leite}                                 │
│  ...                                                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASSO 1: Gerar candidatos de tamanho 1 (C₁)               │
│  Contar suporte de cada item individualmente                 │
│                                                              │
│  {arroz}=25%  {feijão}=21%  {pão}=10%  {sal}=9%  ...       │
└─────────────────────────────────────────────────────────────┘
                          │
          Filtrar por min_support (ex: 5%)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASSO 2: Itemsets frequentes de tamanho 1 (L₁)            │
│  Apenas itens com suporte ≥ min_support                     │
│                                                              │
│  {arroz}=25%  {feijão}=21%  {pão}=10%  ...                 │
└─────────────────────────────────────────────────────────────┘
                          │
               Combinar pares de L₁
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASSO 3: Candidatos de tamanho 2 (C₂)                     │
│  {arroz,feijão}  {arroz,pão}  {feijão,sal}  ...            │
│                                                              │
│  → Aplicar poda: subconjuntos infrequentes são removidos    │
│  → Filtrar novamente por min_support                        │
└─────────────────────────────────────────────────────────────┘
                          │
              Repetir para k = 3, 4, ...
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PASSO 4: Gerar Regras de Associação                        │
│                                                              │
│  Para cada itemset frequente {A, B, C}:                     │
│    A → {B,C}  |  B → {A,C}  |  {A,B} → C  | ...           │
│                                                              │
│  Filtrar por min_confidence e ordenar por Lift              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Como foi Aplicado neste Projeto

Este projeto adapta o Apriori para um caso de **detecção de anomalias** em compras de supermercado. A lógica segue 3 etapas principais:

### Etapa 1 — Aprender o "Normal" com Apriori

O algoritmo Apriori é executado sobre o dataset de transações para descobrir **quais combinações de produtos são frequentes** (compras esperadas e comuns).

```python
# Exemplo de itemsets aprendidos:
{ arroz, feijão }         → suporte: 20%  (normal)
{ shampoo, condicionador} → suporte: 15%  (normal)
{ pão_de_forma, queijo }  → suporte: 10%  (normal)
```

Esses itemsets representam o **comportamento padrão** dos clientes.

### Etapa 2 — Calcular Score de Anomalia

Para cada nova transação, calcula-se um **score de anomalia** baseado no suporte médio dos seus subconjuntos nos itemsets frequentes:

```
                         1
Score(T) = 1 - ─────────────────────────────────────────
                avg( Suporte(S) para S ⊆ T, S ∈ Frequentes )
```

- Se **todos os subconjuntos** da transação são frequentes → score próximo de **0** (normal)
- Se **nenhum subconjunto** é frequente (ex: itens de luxo nunca vistos) → score = **1.0** (anômalo)

```
Transação { arroz, feijão, óleo }        → score: 0.75 ✅ normal
Transação { caviar, trufa, filé_mignon } → score: 1.00 🚨 anomalia
```

### Etapa 3 — Threshold de Detecção por Percentil

O sistema define automaticamente um **threshold** baseado na distribuição dos scores:

```
threshold = percentil(scores de todas as transações, p=90)
```

Transações com score **acima do threshold** são classificadas como **anômalas**. Esse método é auto-adaptativo: não depende de um valor fixo pré-definido.

### Diagrama do Fluxo Completo

```
  Dataset de Compras
         │
         ▼
  ┌─────────────┐      ┌──────────────────────┐
  │  Apriori    │─────►│ Itemsets Frequentes   │
  │  (apriori.py)│     │ Regras de Associação  │
  └─────────────┘      └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Score de Anomalia   │
                        │ (anomaly_detector.py)│
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
             Score < threshold             Score ≥ threshold
             ✅ NORMAL                     🚨 ANOMALIA
```

---

## 📁 Estrutura do Projeto

```
anomaly_detection/
│
├── main.py               # Ponto de entrada — pipeline completo
├── data_generator.py     # Gerador de transações sintéticas (normais + anômalas)
├── apriori.py            # Implementação manual do algoritmo Apriori
├── anomaly_detector.py   # Cálculo de scores e detecção de anomalias
├── visualizer.py         # Relatórios em terminal + gráficos PNG (matplotlib)
├── __init__.py           # Definição do pacote Python
└── requirements.txt      # Dependências (matplotlib)
```

### Responsabilidade de cada módulo

| Módulo | Responsabilidade |
|--------|-----------------|
| `data_generator.py` | Cria transações de compras realistas com padrões normais e anômalos conhecidos (ground truth) |
| `apriori.py` | Implementa o algoritmo Apriori do zero: geração de candidatos, contagem de suporte, poda e geração de regras |
| `anomaly_detector.py` | Calcula o score de anomalia por cobertura de itemsets frequentes e aplica threshold por percentil |
| `visualizer.py` | Exibe relatórios formatados no terminal com barras de progresso e gera gráficos PNG |
| `main.py` | Orquestra todo o pipeline e expõe argumentos de linha de comando |

---

## ▶️ Como Executar

### Pré-requisitos

- Python 3.8+
- `matplotlib` (opcional, apenas para gráficos)

```bash
# Instalar dependências (opcional)
pip install matplotlib
```

### Executar o sistema

```bash
# Entrar no diretório do módulo
cd anomaly_detection

# Rodar com configurações padrão
python3 main.py

# Rodar gerando gráficos PNG na pasta ./graficos/
python3 main.py --graficos

# Personalizar parâmetros
python3 main.py --normais 300 --anomalas 30 --suporte 0.04 --confianca 0.45 --percentil 92
```

> ⚠️ **Importante:** Execute sempre a partir **dentro** da pasta `anomaly_detection/`, não pelo `__init__.py` diretamente.

---

## 📊 Exemplo de Saída

```
═════════════════════════════════════════════════════════════════
  🛒  SISTEMA DE DETECÇÃO DE ANOMALIAS EM COMPRAS
       Baseado no Algoritmo Apriori — Python
═════════════════════════════════════════════════════════════════

  📊 RESUMO DO DATASET
  Total de transações : 220
  ✅ Normais          : 200 (90.9%)
  🚨 Anômalas (reais) : 20  (9.1%)

  📊 TOP 15 ITEMSETS FREQUENTES
  {arroz}                    25.00%  ███████░░░░
  {feijão}                   20.91%  ██████░░░░░
  {arroz, feijão}            20.45%  ██████░░░░░

  📊 TOP 10 REGRAS DE ASSOCIAÇÃO (por Lift)
  {presunto} → {pão_de_forma, queijo}    Sup:5.9% Conf:100% Lift:16.9

  📊 ANOMALIAS DETECTADAS (threshold = 0.9364)
   ID    Score  Barra                  Itens
    42   1.000  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  🚨 caviar, filé_mignon, salmão...
         ↳ Motivo: Compra de luxo em horário incomum

  📊 MÉTRICAS DE AVALIAÇÃO
  Precisão  : 85.00%  █████████████████████████░░░░░
  Recall    : 80.00%  ████████████████████████░░░░░░
  F1-Score  : 82.35%  ████████████████████████░░░░░░
```

---

## 🎛️ Parâmetros Disponíveis

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--normais` | `200` | Número de transações normais geradas |
| `--anomalas` | `20` | Número de transações anômalas geradas |
| `--suporte` | `0.05` | Suporte mínimo do Apriori (5%) |
| `--confianca` | `0.40` | Confiança mínima para regras (40%) |
| `--percentil` | `90.0` | Percentil de corte para threshold de anomalia |
| `--top-regras` | `10` | Número de regras a exibir no relatório |
| `--graficos` | `False` | Gerar e salvar gráficos PNG (requer matplotlib) |

---

## 📖 Referências

- Agrawal, R., & Srikant, R. (1994). **Fast Algorithms for Mining Association Rules**. VLDB Conference.
- Han, J., Kamber, M., & Pei, J. (2011). **Data Mining: Concepts and Techniques**. Morgan Kaufmann.
- Tan, P.-N., Steinbach, M., & Kumar, V. (2005). **Introduction to Data Mining**. Addison-Wesley.