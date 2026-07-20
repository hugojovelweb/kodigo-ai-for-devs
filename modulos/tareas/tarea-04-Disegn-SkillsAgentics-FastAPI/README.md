# Diseño e Integración de Skills Agénticas en FastAPI
### Hugo Ernesto Jovel Hernández
### AI For Developers 01

Proyecto individual que integra una API REST modular en FastAPI con una skill basada en el estándar **Agent Skills**. La solución es autocontenida: no usa modelos ni servicios externos; sus resultados son cálculos locales, verificables y deterministas.

## Funcionalidad

| Método | Ruta | Función |
| --- | --- | --- |
| `GET` | `/health` | Confirma disponibilidad y versión. |
| `POST` | `/v1/text/analyze` | Analiza texto: estadísticas, resumen extractivo o palabras clave. |

Ejemplo de cuerpo para el endpoint de análisis:

```json
{
  "text": "FastAPI permite crear APIs rápidas y documentadas.",
  "mode": "statistics",
  "max_response_chars": 500
}
```

Los modos permitidos son `statistics`, `summary` y `keywords`. La documentación OpenAPI interactiva se publica automáticamente en `http://127.0.0.1:8000/docs`.

## Arquitectura y responsabilidades

```text
app/
├── main.py                   # composición, metadatos y manejo uniforme de errores 422
├── config.py                 # configuración centralizada
├── schemas.py                # contratos Pydantic y validación de entrada
├── api/routes.py             # capa HTTP: endpoints
└── services/text_analysis.py # dominio: lógica pura y testeable
tests/test_api.py             # pruebas de integración
.github/skills/
└── fastapi-safe-text-analysis/SKILL.md
```

La ruta delega en un servicio, evitando mezclar protocolo HTTP con reglas de negocio. Los esquemas validan el tipo, el rango y el caso de texto compuesto solamente por espacios. Los errores de validación se normalizan a una respuesta HTTP 422 con `error`, `message` y `details`, de forma que un agente pueda corregir la solicitud.

## Skill personalizada e integración agéntica

La skill se encuentra en `.github/skills/fastapi-safe-text-analysis/SKILL.md`. Es un directorio de skill con archivo `SKILL.md`, cabecera YAML y los metadatos requeridos `name` y `description`, seguido de instrucciones Markdown.

La descripción hace que se active ante solicitudes de conteo, resumen o extracción de términos. Al activarse, la skill modifica explícitamente el comportamiento del agente:

1. Mapea la intención del usuario a un único modo permitido.
2. Valida localmente que el texto sea no vacío y tenga como máximo 2000 caracteres.
3. Exige verificar `GET /health` antes de la primera llamada y después hacer `POST /v1/text/analyze` con JSON estricto.
4. Indica cómo actuar ante un 422, sin repetir una solicitud inválida.
5. Trata el texto como datos y prohíbe obedecer instrucciones incrustadas, revelar secretos o inventar capacidades.
6. Obliga a declarar que el resultado no equivale a validación factual ni a recomendación profesional.

Así se demuestra que una skill no es un endpoint: es una guía reutilizable que condiciona de forma semántica, segura y auditable la decisión y la interacción del agente con la API.

## Instalación y ejecución

Requiere Python 3.10+.

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Ejemplo en PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/text/analyze `
  -ContentType 'application/json' `
  -Body '{"text":"FastAPI crea APIs rápidas. FastAPI las documenta.","mode":"keywords"}'
```

Pruebas automatizadas:

```bash
pytest -q
```

Las pruebas verifican disponibilidad, conteos esperados y el contrato de error 422 cuando el texto está vacío.

Validación final o si hay lanzadores rotos:

```python -m pytest -q
uvicorn app.main:app --reload``` 

### Si hay error: 
 #Solución inmediata, sin usar el lanzador roto:
 python -m uvicorn app.main:app --reload

 #Para corregir de raiz ejecutar uno por uno de las siguientes líneas:
 
 #deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install --upgrade "starlette[full]"
python -m uvicorn app.main:app --reload



## Evidencia de uso consciente de herramientas de IA

La IA se utilizó como apoyo para proponer la estructura inicial, ejemplos y redacción de la skill. Cada sugerencia se revisó y ajustó antes de incorporarla: se comprobó la separación ruta/servicio/esquema, se conservaron dependencias mínimas, se añadió un validador de texto en blanco, se estandarizó el error 422 y se escribieron pruebas de integración. También se contrastó la forma de la skill con la especificación pública de Agent Skills: un directorio con `SKILL.md` que declara al menos `name` y `description`.

Decisiones técnicas deliberadas: no hay API keys, el texto no se envía a terceros, las operaciones son transparentes y la skill delimita lo que el agente puede afirmar. Por ello la IA acelera el diseño, pero el resultado es validado, explicable y controlado por el estudiante.

## Demostración sugerida

1. Iniciar el servidor y abrir `/docs`.
2. Ejecutar una solicitud válida por cada modo.
3. Enviar `{"text":"   "}` y comprobar la respuesta 422 estructurada.
4. Mostrar `SKILL.md` y explicar el mapeo intención → modo → endpoint.
5. Ejecutar `pytest -q`.

## Referencias

- [Agent Skills Specification](https://agentskills.io/specification)
- [GitHub Docs: About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
