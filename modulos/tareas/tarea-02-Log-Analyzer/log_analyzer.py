#!/usr/bin/env python3
"""
log_analyzer.py
================

Actividad: "IA como Herramienta, no como Autor: Desarrollo Guiado y
Validado de un Script en Python" By Hugo Ernesto Jovel Hernandez

Descripción general
--------------------
Este script lee un archivo de texto que simula un log de eventos de una
aplicación, clasifica cada línea según su nivel de severidad (INFO,
WARNING, ERROR), valida si contiene una fecha bien formateada, y genera
un resumen estadístico que se imprime en consola.

NOTA SOBRE EL USO DE IA (transparencia exigida por la actividad)
------------------------------------------------------------------
- La IA (Copilot / Claude) fue usada como apoyo para:
    * Proponer la expresión regular inicial que separa severidad, fecha
      y mensaje.
    * Sugerir la estructura general de funciones (separar parseo,
      validación y resumen).
    * Explicar el funcionamiento de `datetime.strptime` para validar
      fechas reales (por ejemplo, para rechazar "2025-13-40").
- Las siguientes decisiones NO fueron delegadas a la IA, sino tomadas
  explícitamente por el estudiante (ver también el documento de
  reflexión técnica adjunto):
    1. Qué se considera "línea mal formateada" (criterio de negocio).
    2. Qué hacer cuando falta información: se decidió CONTAR la línea
       en el total de eventos y en su severidad si esta es válida,
       pero además marcarla como "malformada" si le falta fecha válida
       o si la severidad no es reconocida. No se descartan líneas.
    3. Qué casos borde se manejan (líneas vacías, severidad desconocida,
       fecha con formato correcto pero valor imposible, líneas sin
       corchetes) y cuáles quedan fuera de alcance (múltiples fechas en
       una misma línea, zonas horarias, milisegundos).
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y CONSTANTES
# ---------------------------------------------------------------------------

# Decisión del estudiante: se acepta únicamente el formato de fecha
# AAAA-MM-DD porque es el que aparece en los ejemplos de la actividad.
# La IA sugirió inicialmente soportar también "DD/MM/AAAA", pero se
# descartó para no ampliar el alcance sin necesidad (ver reflexión).
DATE_FORMAT = "%Y-%m-%d"
DATE_REGEX = re.compile(r"\d{4}-\d{2}-\d{2}")

# Decisión del estudiante: estos son los únicos niveles de severidad
# válidos. Cualquier otro valor entre corchetes (p. ej. [DEBUG] o
# [CRITICAL]) se considera severidad NO reconocida y la línea se
# marca como malformada, en lugar de ignorarla silenciosamente.
SEVERIDADES_VALIDAS = ("INFO", "WARNING", "ERROR")

# Regex que separa: [SEVERIDAD] (opcional) + fecha (opcional) + mensaje.
# La IA propuso una primera versión de esta expresión regular; el
# estudiante la revisó, la probó contra casos borde y la ajustó para
# que la severidad y la fecha fueran ambas opcionales (porque el
# enunciado muestra líneas sin fecha, como el ejemplo de WARNING).
LINE_REGEX = re.compile(
    r"^\s*(?:\[(?P<severidad>[A-Za-z]+)\])?"   # [SEVERIDAD] opcional
    r"\s*(?P<fecha>\d{4}-\d{2}-\d{2})?"        # fecha opcional
    r"\s*(?P<mensaje>.*)$"                      # resto = mensaje
)


# ---------------------------------------------------------------------------
# 2. ESTRUCTURA DE DATOS
# ---------------------------------------------------------------------------

@dataclass
class EventoLog:
    """Representa una línea del log ya analizada."""
    linea_original: str
    numero_linea: int
    severidad: str | None = None
    severidad_valida: bool = False
    fecha_texto: str | None = None
    fecha_valida: bool = False
    mensaje: str = ""
    es_malformada: bool = False
    motivos_malformacion: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 3. FUNCIONES DE VALIDACIÓN
# ---------------------------------------------------------------------------

def validar_fecha(fecha_texto: str | None) -> bool:
    """
    Valida que la fecha exista y sea una fecha REAL (no solo que tenga
    el formato correcto). Por ejemplo, "2025-13-40" tiene el formato
    AAAA-MM-DD pero no es una fecha válida (mes 13, día 40).

    Decisión del estudiante: usar datetime.strptime en lugar de solo
    el regex, porque el regex únicamente valida forma, no validez real.
    Esta distinción fue explicada por la IA a pedido del estudiante,
    pero la decisión de aplicarla como criterio de "malformación" es
    del estudiante.
    """
    if not fecha_texto:
        return False
    try:
        datetime.strptime(fecha_texto, DATE_FORMAT)
        return True
    except ValueError:
        return False


def severidad_reconocida(severidad_texto: str | None) -> bool:
    """
    Determina si la severidad extraída es una de las reconocidas
    (INFO, WARNING, ERROR). Se normaliza a mayúsculas porque el
    estudiante decidió que el análisis no debe ser sensible a
    mayúsculas/minúsculas (ej. "[info]" también debe reconocerse).
    """
    if not severidad_texto:
        return False
    return severidad_texto.upper() in SEVERIDADES_VALIDAS


# ---------------------------------------------------------------------------
# 4. PARSEO DE UNA LÍNEA
# ---------------------------------------------------------------------------

def analizar_linea(linea: str, numero_linea: int) -> EventoLog | None:
    """
    Analiza una línea individual del log y devuelve un objeto EventoLog.

    Devuelve None si la línea está completamente vacía (solo espacios),
    porque el estudiante decidió que las líneas en blanco NO cuentan
    como eventos ni como errores: simplemente se ignoran por no
    representar ningún evento real. Este es un caso borde explícito.
    """
    linea_limpia = linea.rstrip("\n")

    if linea_limpia.strip() == "":
        return None  # Caso borde: línea vacía -> se ignora, no es un evento

    evento = EventoLog(linea_original=linea_limpia, numero_linea=numero_linea)

    match = LINE_REGEX.match(linea_limpia)
    if not match:
        # En la práctica, con el regex actual esto casi no debería
        # ocurrir (el "mensaje" captura cualquier resto de texto),
        # pero se deja el control explícito por robustez y para dejar
        # constancia de que el caso fue considerado.
        evento.es_malformada = True
        evento.motivos_malformacion.append("Formato de línea irreconocible")
        evento.mensaje = linea_limpia
        return evento

    severidad_cruda = match.group("severidad")
    fecha_cruda = match.group("fecha")
    mensaje = match.group("mensaje").strip()

    # --- Severidad ---
    evento.severidad = severidad_cruda.upper() if severidad_cruda else None
    evento.severidad_valida = severidad_reconocida(severidad_cruda)
    if severidad_cruda is None:
        evento.es_malformada = True
        evento.motivos_malformacion.append("Falta nivel de severidad")
    elif not evento.severidad_valida:
        evento.es_malformada = True
        evento.motivos_malformacion.append(
            f"Severidad no reconocida: '{severidad_cruda}'"
        )

    # --- Fecha ---
    evento.fecha_texto = fecha_cruda
    evento.fecha_valida = validar_fecha(fecha_cruda)
    if fecha_cruda is None:
        evento.es_malformada = True
        evento.motivos_malformacion.append("Falta fecha")
    elif not evento.fecha_valida:
        evento.es_malformada = True
        evento.motivos_malformacion.append(f"Fecha inválida: '{fecha_cruda}'")

    # --- Mensaje ---
    evento.mensaje = mensaje
    if mensaje == "":
        # Caso borde: línea con severidad y/o fecha pero sin mensaje.
        # Decisión del estudiante: se considera malformada porque un
        # evento de log sin mensaje no aporta información útil.
        evento.es_malformada = True
        evento.motivos_malformacion.append("Falta mensaje del evento")

    return evento


# ---------------------------------------------------------------------------
# 5. LECTURA Y PROCESAMIENTO DEL ARCHIVO
# ---------------------------------------------------------------------------

def procesar_archivo(ruta_archivo: str) -> list[EventoLog]:
    """
    Lee el archivo línea por línea y devuelve la lista de eventos
    analizados. Se decidió leer el archivo completo en memoria (en
    lugar de usar streaming) porque el caso de uso son archivos de
    log de tamaño moderado (registros de una sola aplicación), no
    logs masivos de producción; esto simplifica el código sin
    sacrificar el objetivo de la actividad.
    """
    eventos: list[EventoLog] = []

    with open(ruta_archivo, "r", encoding="utf-8", errors="replace") as f:
        for numero_linea, linea in enumerate(f, start=1):
            evento = analizar_linea(linea, numero_linea)
            if evento is not None:
                eventos.append(evento)

    return eventos


# ---------------------------------------------------------------------------
# 6. GENERACIÓN DEL RESUMEN
# ---------------------------------------------------------------------------

def generar_resumen(eventos: list[EventoLog]) -> dict:
    """
    Construye un diccionario de resumen a partir de la lista de eventos.

    Decisión del estudiante sobre "conteo por tipo": un evento se
    cuenta en su categoría de severidad (INFO/WARNING/ERROR) siempre
    que la severidad haya sido reconocida, INDEPENDIENTEMENTE de si la
    línea también está marcada como malformada por otro motivo (por
    ejemplo, fecha inválida). Así, "líneas malformadas" y "conteo por
    severidad" son dos métricas distintas y no mutuamente excluyentes,
    lo cual se explica en el documento de reflexión.
    """
    resumen = {
        "total_eventos": len(eventos),
        "conteo_por_severidad": {sev: 0 for sev in SEVERIDADES_VALIDAS},
        "severidad_desconocida": 0,
        "lineas_malformadas": 0,
        "detalle_malformadas": [],  # (numero_linea, motivos, linea_original)
    }

    for evento in eventos:
        if evento.severidad_valida:
            resumen["conteo_por_severidad"][evento.severidad] += 1
        else:
            resumen["severidad_desconocida"] += 1

        if evento.es_malformada:
            resumen["lineas_malformadas"] += 1
            resumen["detalle_malformadas"].append(
                (evento.numero_linea, evento.motivos_malformacion, evento.linea_original)
            )

    return resumen


# ---------------------------------------------------------------------------
# 7. PRESENTACIÓN EN CONSOLA
# ---------------------------------------------------------------------------

def imprimir_resumen(resumen: dict, ruta_archivo: str) -> None:
    """Imprime el resumen de forma clara y legible en consola."""
    ancho = 60
    print("=" * ancho)
    print(" RESUMEN DE ANÁLISIS DE LOG".center(ancho))
    print("=" * ancho)
    print(f"Archivo analizado: {ruta_archivo}")
    print(f"Total de eventos procesados: {resumen['total_eventos']}")
    print("-" * ancho)
    print("Eventos por tipo de severidad:")
    for severidad, cantidad in resumen["conteo_por_severidad"].items():
        print(f"   {severidad:<10}: {cantidad}")
    print(f"   {'DESCONOCIDA':<10}: {resumen['severidad_desconocida']}")
    print("-" * ancho)
    print(f"Líneas mal formateadas o incompletas: {resumen['lineas_malformadas']}")

    if resumen["detalle_malformadas"]:
        print("-" * ancho)
        print("Detalle de líneas malformadas:")
        for numero_linea, motivos, linea_original in resumen["detalle_malformadas"]:
            print(f"   Línea {numero_linea}: {linea_original!r}")
            for motivo in motivos:
                print(f"        -> {motivo}")

    print("=" * ancho)


# ---------------------------------------------------------------------------
# 8. SELECCIÓN DE ARCHIVO POR EL USUARIO
# ---------------------------------------------------------------------------

def seleccionar_archivo() -> str:
    """
    Permite al usuario seleccionar el archivo a analizar.

    Decisión del estudiante: se prioriza el argumento de línea de
    comandos (sys.argv[1]) porque es la forma más simple y portable de
    "seleccionar un archivo" sin depender de librerías gráficas (que
    pueden no estar disponibles en todos los entornos, p. ej. un
    servidor sin interfaz gráfica). Si no se pasa argumento, se le
    pide la ruta al usuario por consola. Esto cumple el requisito de
    "el programa debe permitir seleccionar el archivo a analizar" sin
    añadir una dependencia externa innecesaria (framework opcional
    "solo si el proyecto lo necesitase", y aquí no se necesita).
    """
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        ruta = input("Ingrese la ruta del archivo de log a analizar: ").strip()

    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    return ruta


# ---------------------------------------------------------------------------
# 9. PUNTO DE ENTRADA
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        ruta_archivo = seleccionar_archivo()
    except FileNotFoundError as error:
        print(f"Error: {error}")
        sys.exit(1)

    eventos = procesar_archivo(ruta_archivo)
    resumen = generar_resumen(eventos)
    imprimir_resumen(resumen, ruta_archivo)


if __name__ == "__main__":
    main()
