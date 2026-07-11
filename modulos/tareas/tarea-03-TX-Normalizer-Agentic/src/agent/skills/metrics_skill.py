"""
metrics_skill.py
-----------------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Skill de solo lectura sobre las métricas ya calculadas por
MetricsCalculator (src/metrics.py). No recalcula nada: expone el
resultado del pipeline como capacidad consultable por el agente.
"""

from agent.skill_base import Skill


class MetricsSkill(Skill):
    name = "obtener_metricas"
    description = (
        "Devuelve las métricas generales del último procesamiento: total de "
        "transacciones, porcentaje de válidas/inválidas, conteo por estado, "
        "por moneda, por fuente y los motivos de invalidez más frecuentes. "
        "Úsala para preguntas como '¿cuántas transacciones fallaron?' o "
        "'dame un resumen general'."
    )
    parameters = {"type": "object", "properties": {}}

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def run(self) -> dict:
        return self.pipeline.metrics
