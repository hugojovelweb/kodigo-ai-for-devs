# TX Normalizer Agéntico — Refactorización y Personalización mediante Skills Propias
### Hugo Ernesto Jovel Hernandez

Refactorización del proyecto **TX Normalizer** (normalización y validación de
transacciones multifuente) hacia una **arquitectura agéntica basada en
skills**, manteniendo el pipeline determinístico original como capa de
dominio y agregando un **agente orquestador** que interpreta lenguaje
natural y despacha la ejecución a la skill correspondiente.

## 1. Objetivo de la refactorización

El proyecto base ya presentaba una separación de responsabilidades correcta
a nivel de módulos (`loader`, `normalizer`, `validator`, `metrics`,
`pipeline`), pero la interacción con el usuario dependía de un **menú fijo
y acoplado a opciones numéricas** (`cli.py`). No existía ningún mecanismo de
personalización del comportamiento del agente ni una forma de exponer las
capacidades del sistema como unidades reutilizables e independientes.

Esta refactorización aborda tres puntos:

1. **Lógica monolítica identificada:** el enrutamiento de la interacción
   (qué hacer según la opción del usuario) vivía embebido en `cli.py`,
   mezclado con la presentación (impresión en consola). No había forma de
   invocar una capacidad del sistema sin pasar por el menú.
2. **Separación de lógica, configuración y comportamiento:** se introduce
   una capa `src/agent/` que separa *interpretación de intención*
   (`agent.py`) de *ejecución de la capacidad* (cada `skill`), sin tocar la
   capa de dominio (`normalizer.py`, `validator.py`, `metrics.py`, que
   permanecen intactos).
3. **Skills propias e integración en un agente personalizado:** cada
   capacidad del sistema se encapsuló como una skill independiente,
   documentada, con su propio esquema de entrada, reutilizable desde
   cualquier interfaz (CLI, tests, u otro agente futuro).

## 2. Arquitectura resultante

```
tx_normalizer_agentic/
├── main.py                        # Punto de entrada (agente por defecto, --classic = menú previo)
├── requirements.txt
├── .env.example
├── config/
│   └── rules.json                 # Reglas de negocio (sin cambios)
├── data/
│   ├── transacciones.json
│   └── transacciones_validas.json
└── src/
    ├── models.py                  # Dominio: esquema normalizado (sin cambios)
    ├── loader.py                  # Dominio: lectura de archivos (sin cambios)
    ├── normalizer.py              # Dominio: detección de fuente + transformación (sin cambios)
    ├── validator.py               # Dominio: reglas de validez de negocio (sin cambios)
    ├── metrics.py                 # Dominio: cálculo de métricas (sin cambios)
    ├── pipeline.py                # Orquestador de dominio: carga -> normaliza -> valida -> métricas
    ├── cli.py                     # NUEVA interfaz: conversacional, delega en el agente
    ├── classic_menu.py            # Interfaz previa a la refactorización (referencia comparativa)
    └── agent/
        ├── skill_base.py          # Contrato común de toda skill (interfaz)
        ├── agent.py                # TransactionAgent: interpreta intención y despacha
        └── skills/
            ├── query_skill.py      # Filtrar transacciones por estado/moneda/ID
            ├── metrics_skill.py    # Exponer métricas agregadas
            ├── invalid_skill.py    # Auditoría de transacciones inválidas
            ├── export_skill.py     # Exportar resultados a JSON
            └── reload_skill.py     # Recargar datos desde otro archivo
```

### Principio de diseño

```
Interfaz (cli.py)  →  Agente (agent.py)  →  Skill (skills/*.py)  →  Dominio (pipeline/normalizer/validator/metrics)
```

Cada capa conoce únicamente a la capa inmediatamente inferior. El agente no
sabe *cómo* se calcula una métrica ni *cómo* se filtra una transacción:
solo sabe que existe una skill llamada `obtener_metricas` o
`filtrar_transacciones` y delega en ella.

## 3. Skills implementadas

| Skill | Responsabilidad única | Parámetros |
|---|---|---|
| `filtrar_transacciones` | Filtrar transacciones válidas | `status`, `currency`, `id_contains` |
| `obtener_metricas` | Exponer métricas agregadas del pipeline | — |
| `ver_transacciones_invalidas` | Auditoría de transacciones rechazadas y su motivo | — |
| `exportar_resultados` | Persistir válidas/inválidas/métricas en JSON | `output_path` |
| `recargar_datos` | Re-ejecutar el pipeline, opcionalmente con otro archivo | `data_path` |

Cada skill hereda de `Skill` (`skill_base.py`), que exige implementar
`run(**kwargs)` y expone `as_tool_spec()` para convertirse automáticamente
en una definición de *tool* consumible por la API de Claude (tool use /
function calling). **Agregar una skill nueva no requiere modificar el
agente**: basta con crear la clase y registrarla en `skills/__init__.py`.

## 4. Personalización del agente (`TransactionAgent`)

`TransactionAgent` (`src/agent/agent.py`) opera en dos modos:

- **ONLINE** (con `ANTHROPIC_API_KEY` configurada): usa *tool use* real de
  la API de Claude. El modelo recibe la petición en lenguaje natural, el
  listado de skills disponibles (con su `input_schema`) y decide de forma
  autónoma cuál invocar y con qué parámetros, pudiendo encadenar varias
  skills antes de redactar la respuesta final. El `system prompt`
  restringe explícitamente al modelo a no inventar datos fuera de lo que
  devuelvan las skills.
- **OFFLINE** (sin API key): enrutador determinístico por palabras clave,
  con la misma interfaz pública (`agent.handle(texto)`), para que el
  proyecto sea ejecutable y evaluable sin depender de credenciales
  externas. El modo activo se declara explícitamente en consola.

Este diseño permite personalizar el comportamiento del agente (modelo,
prompt del sistema, conjunto de skills habilitadas) sin tocar la capa de
dominio ni la interfaz de usuario.

## 5. Ejecución

```bash
pip install -r requirements.txt

# Modo agente (por defecto)
python main.py
python main.py data/transacciones_validas.json config/rules.json

# Modo online (tool use real)
export ANTHROPIC_API_KEY=sk-ant-...
python main.py

# Interfaz previa a la refactorización (comparación antes/después)
python main.py --classic
```

Ejemplos de peticiones en lenguaje natural una vez iniciado el agente:

```
tú> dame un resumen general
tú> muéstrame las transacciones fallidas en EUR
tú> ¿por qué se rechazaron transacciones?
tú> exporta los resultados a resultado.json
tú> recarga los datos desde data/transacciones_validas.json
```

## 6. Qué se conservó y qué se modificó

| Elemento | Estado |
|---|---|
| `models.py`, `loader.py`, `normalizer.py`, `validator.py`, `metrics.py`, `pipeline.py` | Sin cambios (dominio ya correctamente desacoplado) |
| `config/rules.json` | Sin cambios (configuración externa al código) |
| `cli.py` | Reescrito: de menú numérico a interfaz conversacional delegada en el agente |
| `classic_menu.py` | Código del `cli.py` original, conservado íntegro como referencia comparativa |
| `agent/` | Nuevo: capa de orquestación y skills |

## 7. Uso consciente de la IA

La IA (Claude) se usó como apoyo para: proponer la estructura de la capa
`agent/`, el patrón de `tool use` para el modo online y la redacción de
docstrings. Decisiones tomadas explícitamente por el desarrollador: qué
capacidades del dominio se convierten en skills independientes, el
contrato común (`Skill.run` / `as_tool_spec`), la política de "una skill,
una responsabilidad", y el diseño del modo offline como *fallback*
funcionalmente equivalente para garantizar que el proyecto sea evaluable
sin depender de una API key.
