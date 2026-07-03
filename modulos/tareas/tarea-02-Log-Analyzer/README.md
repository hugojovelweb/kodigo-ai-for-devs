# Analizador de Logs en Python — IA como Herramienta, no como Autor By Hugo Ernesto Jovel Hernandez


## 1. Descripción

`log_analyzer.py` es un script en Python que lee un archivo de texto que
simula un log de eventos de una aplicación, identifica el **nivel de
severidad** (INFO / WARNING / ERROR) y si la línea contiene una **fecha
válida**, y genera un **resumen estadístico** (total de eventos, conteo por
severidad y cantidad de líneas mal formateadas), imprimiéndolo de forma
clara en consola.

## 2. Estructura del proyecto

```
proyecto_log_analyzer/
├── log_analyzer.py              # Script principal
├── README.md                    # Este archivo
├── Reflexion_Tecnica.docx       # Documento de reflexión técnica (1-3 páginas)
└── tests/
    ├── log_bien_formado.txt     # Caso de prueba 1: archivo correcto
    └── log_con_errores.txt      # Caso de prueba 2: archivo con inconsistencias
```

## 3. Requisitos

- Python 3.10 o superior (usa sintaxis `str | None`).
- No requiere librerías externas (solo módulos estándar: `re`, `os`, `sys`,
  `datetime`, `dataclasses`).

## 4. Cómo ejecutarlo

**Opción A — pasando la ruta como argumento:**

```bash
python3 log_analyzer.py tests/log_bien_formado.txt
```

**Opción B — sin argumento (el script la solicita por consola):**

```bash
python3 log_analyzer.py
Ingrese la ruta del archivo de log a analizar: tests/log_con_errores.txt
```

## 5. Reglas de análisis (decisiones tomadas por el estudiante)

| Aspecto | Regla aplicada |
|---|---|
| Formato de fecha aceptado | `AAAA-MM-DD` (según ejemplos del enunciado) |
| Severidades reconocidas | `INFO`, `WARNING`, `ERROR` (no distingue mayúsculas/minúsculas) |
| Severidad ausente o desconocida (p. ej. `[DEBUG]`, `[CRITICAL]`) | Se cuenta como evento, se clasifica en "DESCONOCIDA" y la línea se marca como **malformada** |
| Fecha ausente | La línea se cuenta como evento, pero se marca como **malformada** |
| Fecha con formato correcto pero valor imposible (p. ej. `2025-13-40`, `2025-02-30`) | Se valida con `datetime.strptime`, no solo con expresión regular; se marca como **malformada** |
| Mensaje vacío | Se marca como **malformada** (un evento sin mensaje no aporta información) |
| Línea completamente vacía o solo espacios | Se **ignora**, no se cuenta como evento ni como error (no representa un evento real) |

Ninguna línea se descarta silenciosamente: toda línea no vacía se cuenta en
el total de eventos, y si tiene algún problema, se refleja explícitamente en
el conteo de "líneas malformadas" y en el detalle impreso en consola.

## 6. Evidencia de pruebas

### 6.1 Caso 1 — Archivo bien formado (`tests/log_bien_formado.txt`)

12 líneas, todas con severidad válida, fecha válida y mensaje.

**Resultado esperado:** 12 eventos totales, 0 líneas malformadas, conteo por
severidad correspondiente al contenido del archivo (6 INFO, 3 WARNING, 3
ERROR).

**Resultado obtenido (real, ejecución del script):**

```
Total de eventos procesados: 12
Eventos por tipo de severidad:
   INFO      : 6
   WARNING   : 3
   ERROR     : 3
   DESCONOCIDA: 0
Líneas mal formateadas o incompletas: 0
```

✅ Coincide exactamente con lo esperado.

### 6.2 Caso 2 — Archivo con errores (`tests/log_con_errores.txt`)

13 líneas de texto, de las cuales 2 son líneas en blanco (se ignoran) y 11
son eventos, con los siguientes problemas intencionales: fecha faltante,
fecha con formato válido pero valor imposible (mes 13 y 30 de febrero),
severidad faltante, severidad no reconocida (`DEBUG`, `CRITICAL`), severidad
en minúsculas (`info`, debe reconocerse igual) y una línea con severidad
pero sin fecha ni mensaje.

**Resultado esperado:** 11 eventos totales (las 2 líneas en blanco no
cuentan), 7 líneas malformadas, 3 eventos clasificados como severidad
desconocida.

**Resultado obtenido (real, ejecución del script):**

```
Total de eventos procesados: 11
Eventos por tipo de severidad:
   INFO      : 3
   WARNING   : 2
   ERROR     : 3
   DESCONOCIDA: 3
Líneas mal formateadas o incompletas: 7
```

Con el detalle línea por línea mostrando el motivo exacto de cada
malformación (fecha faltante, fecha inválida, severidad no reconocida,
severidad faltante, mensaje faltante).

✅ Coincide exactamente con lo esperado. Nótese que `[info]` en minúscula
(línea 8) **sí** fue reconocida correctamente como `INFO` y no aparece en el
detalle de líneas malformadas, validando la decisión de normalizar a
mayúsculas antes de comparar.

## 7. Uso de Inteligencia Artificial

Ver el documento `Reflexion_Tecnica.docx` para el detalle completo. En
resumen: la IA se usó como apoyo puntual para proponer una primera versión
de la expresión regular y para explicar el comportamiento de
`datetime.strptime`; todas las reglas de negocio (qué es una línea
malformada, qué severidades son válidas, qué hacer con datos faltantes) y la
estructura final del código fueron decisiones del estudiante, incluyendo la
corrección de una sugerencia incorrecta de la IA (detallada en el
documento).

## 8. Herramientas utilizadas

- Lenguaje: Python 3
- Editor: VS Code
- IA de apoyo: asistente integrado de IA (Copilot / Claude) para sugerencias
  puntuales de código, validadas y corregidas manualmente.

## HUGO ERNESTO JOVEL HERNANDEZ - AI FOR DEVELOPER.
