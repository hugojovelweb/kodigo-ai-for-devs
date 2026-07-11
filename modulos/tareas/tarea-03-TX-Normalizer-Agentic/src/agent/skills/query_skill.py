"""
query_skill.py
---------------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
Skill de consulta/filtrado sobre las transacciones válidas ya
normalizadas. Responsabilidad ÚNICA: aplicar filtros; no normaliza,
no valida, no calcula métricas (eso vive en otras skills).
"""

from agent.skill_base import Skill


class QuerySkill(Skill):
    name = "filtrar_transacciones"
    description = (
        "Filtra transacciones válidas por estado (SUCCESS/FAILED/PENDING), "
        "moneda (código ISO como USD/EUR/GBP/MXN/SVC) y/o coincidencia parcial "
        "de ID. Usa esta skill para cualquier consulta sobre transacciones "
        "existentes, por ejemplo 'transacciones fallidas en EUR' o "
        "'busca la transacción tx_003'."
    )
    parameters = {
        "type": "object",
        "properties": {
            "status": {
                "type": ["string", "null"],
                "description": "SUCCESS, FAILED o PENDING. Omitir para no filtrar por estado.",
            },
            "currency": {
                "type": ["string", "null"],
                "description": "Código ISO de moneda (USD, EUR, GBP, MXN, SVC).",
            },
            "id_contains": {
                "type": ["string", "null"],
                "description": "Subcadena a buscar dentro del ID de la transacción.",
            },
        },
    }

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def run(self, status=None, currency=None, id_contains=None) -> dict:
        resultado = self.pipeline.valid

        if status:
            resultado = [tx for tx in resultado if tx.status == status.upper()]
        if currency:
            resultado = [tx for tx in resultado if tx.currency == currency.upper()]
        if id_contains:
            resultado = [tx for tx in resultado if id_contains.lower() in tx.id.lower()]

        return {
            "total_encontradas": len(resultado),
            "transacciones": [tx.to_dict() for tx in resultado],
        }
