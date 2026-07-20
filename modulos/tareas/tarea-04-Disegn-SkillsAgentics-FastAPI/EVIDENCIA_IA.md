# Evidencia de uso consciente de IA
### Hugo Ernesto Jovel Hernández
### AI For Developers 01

## Registro de apoyo y validación

| Etapa | Apoyo de IA | Validación humana aplicada |
| --- | --- | --- |
| Diseño | Propuesta de estructura modular para FastAPI. | Se separaron configuración, esquemas, rutas y servicios; se evitó lógica de negocio en endpoints. |
| Contrato | Borrador de modelos de entrada y salida. | Se fijaron límites de tamaño, enum cerrado de modos y un validador para texto compuesto solo por espacios. |
| Skill | Borrador de flujo de decisión para el agente. | Se contrastó con Agent Skills: carpeta, `SKILL.md`, front matter YAML con `name` y `description`; se añadieron límites de seguridad y manejo de 422. |
| Calidad | Ideas de pruebas y casos borde. | Se implementaron pruebas para salud, conteos y solicitud inválida; se verificó la sintaxis con `compileall`. |

## Decisiones técnicas verificables

- No se añadió una dependencia de modelo de IA: el análisis es local, reproducible y explicable.
- No se usan claves, tokens ni llamadas a proveedores externos.
- La skill indica al agente que el texto es dato, no una fuente de instrucciones privilegiadas.
- La API declara límites de entrada y ofrece errores estructurados; el agente puede solicitar una corrección sin inventar resultados.
- La documentación y las pruebas forman parte de la definición de terminado.

## Conclusión

La IA se empleó como asistente de diseño y redacción, no como sustituto de la revisión técnica. El código, las reglas de seguridad, los límites, los casos de error y la decisión final de arquitectura fueron examinados y ajustados para cumplir el objetivo académico.
