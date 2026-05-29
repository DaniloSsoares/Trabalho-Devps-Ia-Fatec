"""
__init__.py
-----------
Pacote: anomaly_detection
Sistema de detecção de anomalias em compras via algoritmo Apriori.

NOTA: Execute o sistema pelo main.py, não por este arquivo.
  ✅ Correto:  python anomaly_detection/main.py
  ❌ Errado:   python anomaly_detection/__init__.py
"""

try:
    # Quando importado como pacote (import anomaly_detection)
    from .data_generator import gerar_dataset
    from .apriori import encontrar_itemsets_frequentes, gerar_regras, resumo_apriori
    from .anomaly_detector import calcular_score_anomalia, detectar_anomalias, avaliar_deteccao
except ImportError:
    # Quando o diretório está no sys.path (execução direta interna)
    from data_generator import gerar_dataset
    from apriori import encontrar_itemsets_frequentes, gerar_regras, resumo_apriori
    from anomaly_detector import calcular_score_anomalia, detectar_anomalias, avaliar_deteccao

__all__ = [
    "gerar_dataset",
    "encontrar_itemsets_frequentes",
    "gerar_regras",
    "resumo_apriori",
    "calcular_score_anomalia",
    "detectar_anomalias",
    "avaliar_deteccao",
]
