"""
cli.py
------  ### Hugo Ernesto Jovel Hernandez
Interfaz interactiva por menú (obligatoria según la actividad). No usa
prints "planos" como única salida: permite navegar por menús, aplicar
filtros y exportar resultados.

Responsabilidad ÚNICA: presentación/interacción. No contiene reglas de
normalización ni de validación (delega todo en pipeline.py).
"""

import os
import sys
import json
from pipeline import Pipeline

DEFAULT_DATA = os.path.join(os.path.dirname(__file__), "..", "data", "transacciones.json")
DEFAULT_RULES = os.path.join(os.path.dirname(__file__), "..", "config", "rules.json")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPresiona ENTER para continuar...")


def print_header(title: str):
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_transactions(transactions):
    if not transactions:
        print("(sin resultados)")
        return
    print(f"{'ID':<10}{'MONTO':>10}  {'MONEDA':<7}{'ESTADO':<10}{'FUENTE':<10}{'FECHA (UTC)'}")
    print("-" * 75)
    for tx in transactions:
        print(f"{tx.id:<10}{tx.amount:>10.2f}  {tx.currency:<7}{tx.status:<10}{tx.source:<10}{tx.timestamp}")


def menu_ver_todas(pipeline):
    clear()
    print_header("TODAS LAS TRANSACCIONES VÁLIDAS")
    print_transactions(pipeline.valid)
    pause()


def menu_filtrar_estado(pipeline):
    clear()
    print_header("FILTRAR POR ESTADO")
    estados = ["SUCCESS", "FAILED", "PENDING"]
    for i, e in enumerate(estados, 1):
        print(f"{i}. {e}")
    op = input("Elige un estado (número): ").strip()
    try:
        estado = estados[int(op) - 1]
    except (ValueError, IndexError):
        print("Opción inválida.")
        pause()
        return
    resultado = [tx for tx in pipeline.valid if tx.status == estado]
    clear()
    print_header(f"TRANSACCIONES CON ESTADO = {estado}")
    print_transactions(resultado)
    pause()


def menu_filtrar_moneda(pipeline):
    clear()
    print_header("FILTRAR POR MONEDA")
    monedas = sorted({tx.currency for tx in pipeline.valid})
    if not monedas:
        print("No hay monedas disponibles.")
        pause()
        return
    for i, m in enumerate(monedas, 1):
        print(f"{i}. {m}")
    op = input("Elige una moneda (número): ").strip()
    try:
        moneda = monedas[int(op) - 1]
    except (ValueError, IndexError):
        print("Opción inválida.")
        pause()
        return
    resultado = [tx for tx in pipeline.valid if tx.currency == moneda]
    clear()
    print_header(f"TRANSACCIONES EN {moneda}")
    print_transactions(resultado)
    total = sum(tx.amount for tx in resultado)
    print(f"\nTotal en {moneda}: {total:,.2f}")
    pause()


def menu_buscar_id(pipeline):
    clear()
    print_header("BUSCAR TRANSACCIÓN POR ID")
    query = input("Ingresa el ID (o parte de él): ").strip().lower()
    resultado = [tx for tx in pipeline.valid if query in tx.id.lower()]
    print_transactions(resultado)
    pause()


def menu_metricas(pipeline):
    clear()
    print_header("MÉTRICAS GENERALES")
    m = pipeline.metrics
    print(f"Total procesadas:      {m['total_procesadas']}")
    print(f"Válidas:               {m['total_validas']} ({m['porcentaje_validas']}%)")
    print(f"Inválidas:             {m['total_invalidas']}")
    print("\nConteo por estado:")
    for k, v in m["conteo_por_estado"].items():
        print(f"  {k:<10}{v}")
    print("\nConteo por fuente:")
    for k, v in m["conteo_por_fuente"].items():
        print(f"  {k:<10}{v}")
    print("\nTotales por moneda (transacciones válidas):")
    for k, v in m["totales_por_moneda"].items():
        cnt = m["conteo_por_moneda"].get(k, 0)
        print(f"  {k:<5} {v:>12,.2f}   ({cnt} transacciones)")
    print("\nMotivos de invalidez más frecuentes:")
    if not m["motivos_invalidez_frecuentes"]:
        print("  (ninguno)")
    for k, v in m["motivos_invalidez_frecuentes"].items():
        print(f"  {v:>3}x  {k}")
    pause()


def menu_ver_invalidas(pipeline):
    clear()
    print_header("TRANSACCIONES INVÁLIDAS")
    if not pipeline.invalid:
        print("No hay transacciones inválidas.")
    for inv in pipeline.invalid:
        print(f"- Fuente: {inv.source}")
        print(f"  Motivos: {', '.join(inv.reasons)}")
        print(f"  Registro original: {json.dumps(inv.original_record, ensure_ascii=False)}")
        print("-" * 60)
    pause()


def menu_exportar(pipeline):
    clear()
    print_header("EXPORTAR RESULTADOS NORMALIZADOS")
    out_path = input("Ruta de salida [salida_normalizada.json]: ").strip() or "salida_normalizada.json"
    payload = {
        "transacciones_validas": [tx.to_dict() for tx in pipeline.valid],
        "transacciones_invalidas": [inv.to_dict() for inv in pipeline.invalid],
        "metricas": pipeline.metrics,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Exportado a: {out_path}")
    pause()


def menu_recargar(pipeline):
    clear()
    print_header("RECARGAR DATOS DESDE ARCHIVO")
    ruta = input(f"Ruta del archivo JSON [{pipeline.data_path}]: ").strip()
    if ruta:
        pipeline.data_path = ruta
    try:
        pipeline.reload()
        print("Datos recargados correctamente.")
    except Exception as e:
        print(f"Error al recargar: {e}")
    pause()


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA
    rules_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_RULES

    try:
        pipeline = Pipeline(data_path, rules_path)
        pipeline.run()
    except Exception as e:
        print(f"Error al iniciar el pipeline: {e}")
        sys.exit(1)

    opciones = {
        "1": ("Ver todas las transacciones válidas", menu_ver_todas),
        "2": ("Filtrar por estado", menu_filtrar_estado),
        "3": ("Filtrar por moneda", menu_filtrar_moneda),
        "4": ("Buscar transacción por ID", menu_buscar_id),
        "5": ("Ver métricas generales", menu_metricas),
        "6": ("Ver transacciones inválidas", menu_ver_invalidas),
        "7": ("Exportar resultados normalizados a JSON", menu_exportar),
        "8": ("Recargar datos desde archivo", menu_recargar),
    }

    while True:
        clear()
        print_header("NORMALIZACIÓN Y EXPLORACIÓN DE TRANSACCIONES MULTIFUENTE")
        print(f"Archivo activo: {pipeline.data_path}\n")
        for k, (label, _) in opciones.items():
            print(f"  {k}. {label}")
        print("  0. Salir")
        print()
        choice = input("Selecciona una opción: ").strip()

        if choice == "0":
            print("Saliendo. ¡Hasta luego!")
            break
        elif choice in opciones:
            opciones[choice][1](pipeline)
        else:
            print("Opción no válida.")
            pause()


if __name__ == "__main__":
    main()
