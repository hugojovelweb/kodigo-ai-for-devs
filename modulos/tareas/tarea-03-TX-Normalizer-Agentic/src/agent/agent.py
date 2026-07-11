"""
agent.py
--------
### Hugo Ernesto Jovel Hernandez
-----------------------------------
TransactionAgent: agente personalizado del dominio "normalización de
transacciones". Responsabilidad ÚNICA: interpretar la intención del
usuario (lenguaje natural) y despachar la ejecución a la skill
correspondiente. El agente no contiene reglas de negocio ni de
formato: todo eso vive encapsulado en cada Skill.

Modo de operación:
- ONLINE  (requiere variable de entorno ANTHROPIC_API_KEY): usa "tool use"
  / function calling de la API de Claude para que el modelo decida, a
  partir del lenguaje natural del usuario, qué skill invocar y con qué
  parámetros, y redacte la respuesta final.
- OFFLINE (sin API key): usa un enrutador determinístico por palabras
  clave, para que el proyecto sea ejecutable y evaluable sin depender
  de credenciales externas. El modo activo se informa explícitamente
  en consola.
"""

import os
import json
from typing import List

from agent.skill_base import Skill

try:
    import anthropic
    _ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    _ANTHROPIC_SDK_AVAILABLE = False

DEFAULT_MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-5")

SYSTEM_PROMPT = (
    "Eres el agente del sistema de normalización de transacciones "
    "multifuente. Debes resolver la petición del usuario EXCLUSIVAMENTE "
    "invocando las skills disponibles; nunca inventes transacciones, "
    "montos ni métricas que no provengan del resultado de una skill. "
    "Si la petición no corresponde a ninguna skill, explícalo brevemente. "
    "Responde siempre en español, de forma breve, clara y profesional."
)


class TransactionAgent:
    def __init__(self, skills: List[Skill], pipeline):
        self.skills = {s.name: s for s in skills}
        self.pipeline = pipeline
        self.client = None
        self.online = False

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if _ANTHROPIC_SDK_AVAILABLE and api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
            self.online = True

    # ------------------------------------------------------------------ #
    # Punto de entrada público
    # ------------------------------------------------------------------ #
    def handle(self, user_input: str) -> str:
        if self.online:
            return self._handle_online(user_input)
        return self._handle_offline(user_input)

    # ------------------------------------------------------------------ #
    # Modo ONLINE: el LLM decide qué skill(s) invocar (tool use real)
    # ------------------------------------------------------------------ #
    def _tool_specs(self):
        return [s.as_tool_spec() for s in self.skills.values()]

    def _handle_online(self, user_input: str) -> str:
        messages = [{"role": "user", "content": user_input}]

        response = self.client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=self._tool_specs(),
            messages=messages,
        )

        # Bucle de tool-use: el modelo puede encadenar varias skills
        # antes de dar la respuesta final en texto.
        max_iteraciones = 5
        while response.stop_reason == "tool_use" and max_iteraciones > 0:
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    skill = self.skills.get(block.name)
                    if skill is None:
                        resultado = {"error": f"Skill desconocida: {block.name}"}
                    else:
                        try:
                            resultado = skill.run(**block.input)
                        except Exception as exc:  # skill falla -> se informa al modelo
                            resultado = {"error": str(exc)}
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(resultado, ensure_ascii=False, default=str),
                        }
                    )

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=self._tool_specs(),
                messages=messages,
            )
            max_iteraciones -= 1

        textos = [b.text for b in response.content if b.type == "text"]
        return "\n".join(textos).strip() or "(el agente no devolvió texto)"

    # ------------------------------------------------------------------ #
    # Modo OFFLINE: enrutador determinístico por palabras clave
    # ------------------------------------------------------------------ #
    def _handle_offline(self, user_input: str) -> str:
        texto = user_input.lower().strip()

        if any(p in texto for p in ("métrica", "metrica", "resumen", "estadística", "estadistica")):
            return self._formatear(self.skills["obtener_metricas"].run())

        if any(p in texto for p in ("inválida", "invalida", "rechazad", "fallo de normaliz")):
            return self._formatear(self.skills["ver_transacciones_invalidas"].run())

        if any(p in texto for p in ("exporta", "guarda", "descarga")):
            return self._formatear(self.skills["exportar_resultados"].run())

        if any(p in texto for p in ("recarga", "otro archivo", "vuelve a cargar")):
            return self._formatear(self.skills["recargar_datos"].run())

        # Por defecto: consulta/filtrado (intenta detectar estado y moneda)
        status = next((s for s in ("SUCCESS", "FAILED", "PENDING") if s.lower() in texto), None)
        currency = next((c for c in ("USD", "EUR", "GBP", "MXN", "SVC") if c.lower() in texto), None)
        resultado = self.skills["filtrar_transacciones"].run(status=status, currency=currency)
        nota = (
            "\n[modo offline: interpretación limitada por palabras clave; "
            "configure ANTHROPIC_API_KEY para lenguaje natural completo]"
        )
        return self._formatear(resultado) + nota

    @staticmethod
    def _formatear(resultado: dict) -> str:
        return json.dumps(resultado, indent=2, ensure_ascii=False, default=str)
