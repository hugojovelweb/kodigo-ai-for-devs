"""
export_skill.py
-----------------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Skill de efecto lateral (I/O): persiste el resultado del pipeline en
un archivo JSON. Es la única skill autorizada a escribir en disco.
"""

import json
from agent.skill_base import Skill


class ExportSkill(Skill):
    name = "exportar_resultados"
    description = (
        "Exporta a un archivo JSON las transacciones válidas, las inválidas "
        "y las métricas del último procesamiento. Úsala cuando el usuario "
        "pida 'exportar', 'guardar' o 'descargar' los resultados."
    )
    parameters = {
        "type": "object",
        "properties": {
            "output_path": {
                "type": "string",
                "description": "Ruta del archivo de salida. Por defecto: salida_normalizada.json",
            }
        },
    }

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def run(self, output_path: str = "salida_normalizada.json") -> dict:
        payload = {
            "transacciones_validas": [tx.to_dict() for tx in self.pipeline.valid],
            "transacciones_invalidas": [inv.to_dict() for inv in self.pipeline.invalid],
            "metricas": self.pipeline.metrics,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return {"exportado_en": output_path, "estado": "ok"}
