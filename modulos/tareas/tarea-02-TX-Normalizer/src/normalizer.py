"""
normalizer.py
-------------  ### Hugo Ernesto Jovel Hernandez
Responsabilidad ÚNICA: detectar la fuente de cada transacción cruda y
transformarla al esquema normalizado (NormalizedTransaction).

No valida "reglas de negocio" de validez (eso vive en validator.py).
Aquí solo se hacen transformaciones de formato: moneda, monto y fecha.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple

from models import NormalizedTransaction


class NormalizationError(Exception):
    """Se lanza cuando un registro no puede transformarse al esquema común."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class TransactionNormalizer:
    def __init__(self, rules: dict):
        self.rules = rules
        self.status_maps = rules["mapeo_estados"]
        self.date_formats = rules["formatos_fecha"]
        self.symbol_to_code = rules["monedas_soportadas"]["simbolo_a_codigo"]
        self.valid_currencies = set(rules["monedas_soportadas"]["codigos_validos"])

    # ------------------------------------------------------------------ #
    # 1. Detección de fuente
    # ------------------------------------------------------------------ #
    def detect_source(self, record: dict) -> Optional[str]:
        """Detecta la fuente según las llaves presentes en el registro.
        Regla explícita basada en la 'huella' de campos de cada formato."""
        keys = set(record.keys())

        if {"id", "amount", "currency", "timestamp", "status"}.issubset(keys):
            return "source_a"
        if {"transaction_id", "total", "currency_code", "created_at", "state"}.issubset(keys):
            return "source_b"
        if {"ref", "amount", "date", "result"}.issubset(keys):
            return "source_c"
        return None

    # ------------------------------------------------------------------ #
    # 2. Normalización de un registro
    # ------------------------------------------------------------------ #
    def normalize(self, record: dict) -> Tuple[Optional[NormalizedTransaction], list]:
        """Devuelve (transaccion_normalizada_o_None, lista_de_errores)."""
        errors = []
        source = self.detect_source(record)

        if source is None:
            return None, ["Fuente no reconocida: el registro no coincide con ningún esquema conocido"]

        try:
            if source == "source_a":
                tx = self._normalize_source_a(record)
            elif source == "source_b":
                tx = self._normalize_source_b(record)
            else:
                tx = self._normalize_source_c(record)
            return tx, []
        except NormalizationError as e:
            return None, [e.message]

    # ------------------------------------------------------------------ #
    # Normalizadores por fuente
    # ------------------------------------------------------------------ #
    def _normalize_source_a(self, r: dict) -> NormalizedTransaction:
        tx_id = str(r.get("id") or "").strip()
        if not tx_id:
            raise NormalizationError("id vacío en source_a")

        amount = self._to_float(r.get("amount"), "source_a")
        currency = self._normalize_currency(r.get("currency"))
        timestamp = self._parse_date(r.get("timestamp"), "source_a")
        status = self._map_status(r.get("status"), "source_a")

        return NormalizedTransaction(tx_id, round(amount, 2), currency, timestamp, status, "source_a")

    def _normalize_source_b(self, r: dict) -> NormalizedTransaction:
        tx_id = str(r.get("transaction_id") or "").strip()
        if not tx_id:
            raise NormalizationError("transaction_id vacío en source_b")

        # Regla: 'total' viene en centavos (entero) -> dividir entre 100
        raw_total = r.get("total")
        if raw_total is None:
            raise NormalizationError("total ausente en source_b")
        amount = float(raw_total) / 100.0

        currency = self._normalize_currency(r.get("currency_code"))
        timestamp = self._parse_date(r.get("created_at"), "source_b")
        status = self._map_status(r.get("state"), "source_b")

        return NormalizedTransaction(tx_id, round(amount, 2), currency, timestamp, status, "source_b")

    def _normalize_source_c(self, r: dict) -> NormalizedTransaction:
        tx_id = str(r.get("ref") or "").strip()
        if not tx_id:
            raise NormalizationError("ref vacío en source_c")

        raw_amount = r.get("amount")
        amount, symbol_currency = self._parse_symbol_amount(raw_amount)

        currency = symbol_currency
        timestamp = self._parse_date(r.get("date"), "source_c")
        status = self._map_status(r.get("result"), "source_c")

        return NormalizedTransaction(tx_id, round(amount, 2), currency, timestamp, status, "source_c")

    # ------------------------------------------------------------------ #
    # Helpers de transformación
    # ------------------------------------------------------------------ #
    def _to_float(self, value, source: str) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            raise NormalizationError(f"monto no numérico en {source}: {value!r}")

    def _normalize_currency(self, raw) -> str:
        if raw is None:
            raise NormalizationError("moneda ausente")
        code = str(raw).strip().upper()
        if code in self.symbol_to_code.values() or code in self.valid_currencies:
            return code
        # ¿es un símbolo?
        if raw in self.symbol_to_code:
            return self.symbol_to_code[raw]
        raise NormalizationError(f"moneda no soportada: {raw!r}")

    def _parse_symbol_amount(self, raw) -> Tuple[float, str]:
        """Parsea montos tipo '€99,99' -> (99.99, 'EUR')."""
        if raw is None:
            raise NormalizationError("monto ausente en source_c")
        text = str(raw).strip()
        symbol = None
        for s in self.symbol_to_code:
            if text.startswith(s) or text.endswith(s):
                symbol = s
                text = text.replace(s, "")
                break
        if symbol is None:
            raise NormalizationError(f"no se pudo determinar la moneda del monto: {raw!r}")
        text = text.strip().replace(".", "").replace(",", ".") if "," in text else text.strip()
        try:
            amount = float(text)
        except ValueError:
            raise NormalizationError(f"monto con formato inválido en source_c: {raw!r}")
        return amount, self.symbol_to_code[symbol]

    def _parse_date(self, raw, source: str) -> str:
        if not raw:
            raise NormalizationError(f"fecha ausente en {source}")
        fmt = self.date_formats.get(source)
        try:
            if source == "source_c":
                # ISO-8601 nativo, admite sufijo Z
                dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(str(raw), fmt)
                dt = dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            raise NormalizationError(f"formato de fecha inválido en {source}: {raw!r}")

        dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _map_status(self, raw, source: str) -> str:
        if raw is None:
            raise NormalizationError(f"estado ausente en {source}")
        mapping = self.status_maps.get(source, {})
        # Búsqueda case-insensitive tolerante
        if raw in mapping:
            return mapping[raw]
        for k, v in mapping.items():
            if k.lower() == str(raw).lower():
                return v
        raise NormalizationError(f"estado no reconocido en {source}: {raw!r}")
