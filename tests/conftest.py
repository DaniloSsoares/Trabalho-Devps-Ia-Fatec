"""
conftest.py
-----------
Configuração compartilhada do pytest.

Adiciona o diretório `anomaly_detection/` ao sys.path para que os módulos
do pacote (apriori, anomaly_detector, data_generator) possam ser importados
diretamente nos testes — espelhando o que o main.py faz em runtime.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE = os.path.join(RAIZ, "anomaly_detection")

sys.path.insert(0, PACOTE)
