"""
skills/__init__.py
--------------------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Punto único de registro de skills. Agregar una skill nueva al sistema
NO requiere tocar el agente ni la CLI: solo se instancia aquí y queda
disponible automáticamente.
"""

from agent.skills.query_skill import QuerySkill
from agent.skills.metrics_skill import MetricsSkill
from agent.skills.invalid_skill import InvalidSkill
from agent.skills.export_skill import ExportSkill
from agent.skills.reload_skill import ReloadSkill


def build_skills(pipeline):
    """Instancia todas las skills del sistema, conectadas al mismo pipeline."""
    return [
        QuerySkill(pipeline),
        MetricsSkill(pipeline),
        InvalidSkill(pipeline),
        ExportSkill(pipeline),
        ReloadSkill(pipeline),
    ]
