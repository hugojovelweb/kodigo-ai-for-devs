"""
skill_base.py
-------------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Contrato común que debe cumplir toda skill del sistema.

Una "skill" encapsula UNA capacidad concreta del dominio (filtrar,
calcular métricas, exportar, recargar, etc.), expone su propio esquema
de parámetros (input_schema tipo JSON Schema) y sabe ejecutarse a sí
misma. El agente NO conoce reglas de negocio: solo conoce esta interfaz
y delega en la skill correspondiente.

Este desacoplamiento es el núcleo de la refactorización: separa
"decidir qué hacer" (agente) de "cómo hacerlo" (skill).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Skill(ABC):
    name: str = "skill_sin_nombre"
    description: str = ""
    parameters: Dict[str, Any] = {"type": "object", "properties": {}}

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Ejecuta la skill y devuelve un resultado serializable (dict/list/str)."""
        raise NotImplementedError

    def as_tool_spec(self) -> Dict[str, Any]:
        """Convierte la skill a la especificación de 'tool' que consume la
        API de Claude (tool use / function calling)."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
