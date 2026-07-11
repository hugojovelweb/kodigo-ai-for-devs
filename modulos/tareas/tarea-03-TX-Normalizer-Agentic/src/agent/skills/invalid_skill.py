"""
invalid_skill.py
-----------------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Skill de auditoría: expone las transacciones que no pudieron
normalizarse o que no pasaron las reglas de validación, junto con su
motivo. Refleja la política del sistema de "no descartar silenciosamente".
"""

from agent.skill_base import Skill


class InvalidSkill(Skill):
    name = "ver_transacciones_invalidas"
    description = (
        "Devuelve la lista de transacciones inválidas (no normalizables o que "
        "no cumplen las reglas de negocio), incluyendo el motivo de invalidez "
        "y el registro original. Úsala para preguntas de auditoría como "
        "'¿por qué fallaron transacciones?' o '¿qué registros se rechazaron?'."
    )
    parameters = {"type": "object", "properties": {}}

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def run(self) -> dict:
        return {
            "total_invalidas": len(self.pipeline.invalid),
            "detalle": [inv.to_dict() for inv in self.pipeline.invalid],
        }
