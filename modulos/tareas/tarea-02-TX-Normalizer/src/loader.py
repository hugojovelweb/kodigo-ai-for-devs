"""
loader.py
--------- ### Hugo Ernesto Jovel Hernandez
Responsabilidad ÚNICA: leer archivos del disco (JSON de transacciones y
JSON de reglas de configuración). No transforma ni valida datos de negocio.
"""

import json
from pathlib import Path
from typing import List


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def load_transactions(path: str) -> List[dict]:
    data = load_json(path)
    if not isinstance(data, list):
        raise ValueError("El archivo de transacciones debe contener una lista JSON de objetos")
    return data


def load_rules(path: str) -> dict:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("El archivo de reglas debe contener un objeto JSON")
    return data
