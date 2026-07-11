"""
reload_skill.py
-----------------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Skill de efecto lateral: vuelve a ejecutar el pipeline, opcionalmente
contra un archivo de datos distinto. No contiene lógica de
normalización/validación propia; delega en Pipeline.run().
"""

from agent.skill_base import Skill


class ReloadSkill(Skill):
    name = "recargar_datos"
    description = (
        "Vuelve a cargar y procesar las transacciones, opcionalmente desde "
        "una ruta de archivo distinta. Úsala cuando el usuario pida "
        "'recargar', 'usar otro archivo' o 'procesar de nuevo'."
    )
    parameters = {
        "type": "object",
        "properties": {
            "data_path": {
                "type": ["string", "null"],
                "description": "Ruta del nuevo archivo JSON de transacciones. Omitir para recargar el mismo archivo.",
            }
        },
    }

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def run(self, data_path: str = None) -> dict:
        if data_path:
            self.pipeline.data_path = data_path
        self.pipeline.reload()
        return {
            "estado": "recargado",
            "archivo_activo": self.pipeline.data_path,
            "total_validas": len(self.pipeline.valid),
            "total_invalidas": len(self.pipeline.invalid),
        }
