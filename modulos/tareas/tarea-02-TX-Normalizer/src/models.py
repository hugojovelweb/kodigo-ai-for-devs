"""
models.py
---------  ### Hugo Ernesto Jovel Hernandez
Define el ESQUEMA NORMALIZADO final del sistema.

Decisión de diseño (no delegada a la IA): el esquema común elegido es:

    {
        "id": str,            -> identificador original de la fuente (id / transaction_id / ref)
        "amount": float,       -> monto en unidad decimal estándar, 2 decimales
        "currency": str,       -> código ISO 4217 en mayúsculas (USD, EUR, GBP...)
        "timestamp": str,      -> fecha/hora en ISO-8601 UTC ("YYYY-MM-DDTHH:MM:SSZ")
        "status": str,         -> SUCCESS | FAILED | PENDING
        "source": str          -> fuente detectada (source_a / source_b / source_c)
    }

Se eligió este esquema porque:
  - Es agnóstico de la fuente original.
  - Usa tipos primitivos fáciles de filtrar/ordenar en la interfaz.
  - ISO-8601 y ISO 4217 son estándares reconocidos, evitando ambigüedad.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class NormalizedTransaction:
    id: str
    amount: float
    currency: str
    timestamp: str
    status: str
    source: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class InvalidTransaction:
    """Transacción que no pasó la validación. Se conserva el registro original
    y el/los motivo(s) de invalidez, en vez de descartarla silenciosamente."""
    original_record: dict
    source: str
    reasons: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "reasons": self.reasons,
            "original_record": self.original_record,
        }
