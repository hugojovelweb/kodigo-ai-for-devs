"""
cli.py
------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Interfaz conversacional. Responsabilidad ÚNICA: entrada/salida por
consola. No contiene reglas de negocio ni de enrutamiento: todo se
delega en TransactionAgent, que a su vez delega en las skills.

Para la interfaz de menús clásica (previa a la refactorización), ver
classic_menu.py, conservada como referencia para el análisis
comparativo antes/después.
"""

import os
import sys

from pipeline import Pipeline
from agent import TransactionAgent, build_skills

DEFAULT_DATA = os.path.join(os.path.dirname(__file__), "..", "data", "transacciones.json")
DEFAULT_RULES = os.path.join(os.path.dirname(__file__), "..", "config", "rules.json")


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA
    rules_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_RULES

    try:
        pipeline = Pipeline(data_path, rules_path)
        pipeline.run()
    except Exception as e:
        print(f"Error al iniciar el pipeline: {e}")
        sys.exit(1)

    agente = TransactionAgent(build_skills(pipeline), pipeline)

    print("=" * 60)
    print("  AGENTE DE NORMALIZACIÓN DE TRANSACCIONES MULTIFUENTE")
    print("=" * 60)
    print(f"Archivo activo: {pipeline.data_path}")
    modo = "ONLINE (Claude, tool use)" if agente.online else "OFFLINE (enrutador por palabras clave)"
    print(f"Modo del agente: {modo}")
    print("Escribe tu petición en lenguaje natural (o 'salir' para terminar).")
    print("Ejemplos: 'muéstrame las transacciones fallidas en EUR', "
          "'dame un resumen', 'exporta los resultados'.")
    print("-" * 60)

    while True:
        try:
            user_input = input("\ntú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo. ¡Hasta luego!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            print("Saliendo. ¡Hasta luego!")
            break

        respuesta = agente.handle(user_input)
        print(f"\nagente> {respuesta}")


if __name__ == "__main__":
    main()
