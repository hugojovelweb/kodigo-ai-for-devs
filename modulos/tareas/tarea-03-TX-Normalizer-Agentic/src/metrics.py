"""
metrics.py
----------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Responsabilidad ÚNICA: calcular métricas agregadas sobre el resultado
de normalización + validación. No transforma ni valida datos.
"""

from collections import Counter, defaultdict
from typing import List
from models import NormalizedTransaction, InvalidTransaction


class MetricsCalculator:
    def __init__(self, valid: List[NormalizedTransaction], invalid: List[InvalidTransaction], total_raw: int):
        self.valid = valid
        self.invalid = invalid
        self.total_raw = total_raw

    def summary(self) -> dict:
        by_status = Counter(tx.status for tx in self.valid)
        by_currency_totals = defaultdict(float)
        by_currency_count = Counter()
        by_source = Counter(tx.source for tx in self.valid)

        for tx in self.valid:
            by_currency_totals[tx.currency] += tx.amount
            by_currency_count[tx.currency] += 1

        error_reasons = Counter()
        for inv in self.invalid:
            for r in inv.reasons:
                # agrupamos por el primer segmento del motivo (antes de ':')
                key = r.split(":")[0].strip()
                error_reasons[key] += 1

        return {
            "total_procesadas": self.total_raw,
            "total_validas": len(self.valid),
            "total_invalidas": len(self.invalid),
            "porcentaje_validas": round(
                (len(self.valid) / self.total_raw * 100) if self.total_raw else 0, 2
            ),
            "conteo_por_estado": dict(by_status),
            "conteo_por_moneda": dict(by_currency_count),
            "totales_por_moneda": {k: round(v, 2) for k, v in by_currency_totals.items()},
            "conteo_por_fuente": dict(by_source),
            "motivos_invalidez_frecuentes": dict(error_reasons.most_common()),
        }
