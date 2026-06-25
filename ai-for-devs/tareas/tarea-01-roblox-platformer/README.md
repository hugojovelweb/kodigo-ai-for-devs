# 🎮 BLOX JUMP Hugo Jovel – Plataforma Estilo Roblox 2D

Un mini-juego platforma desarrollado con **Python + Pygame** usando IA como copiloto (vibecoding).

---

## ▶️ Cómo ejecutar

```bash
pip install pygame
python juego.py
```

### Controles
| Tecla | Acción |
|-------|--------|
| `←` / `A` | Mover izquierda |
| `→` / `D` | Mover derecha |
| `ESPACIO` / `W` / `↑` | Saltar (doble salto disponible) |
| `R` | Reiniciar desde nivel 1 |
| `ESC` | Salir |

---

## 🎯 Objetivo del juego

Llegar a la **estrella dorada** (✓) al final de cada nivel saltando entre plataformas. Si caes al vacío, pierdes y reintentas. Hay **3 niveles** con dificultad progresiva.

---

## 🧠 Evidencia de Vibecoding

### PROMPT 1 – Estructura base del juego

**Qué se pidió:**
> "Crea un juego plataformero 2D en Python con Pygame. El jugador debe ser un bloque estilo Roblox de color azul con ojos. Debe haber gravedad, salto y colisión con plataformas rojas. La pantalla es 900x600."

**Por qué se usó este prompt:**
Fue el prompt inicial para establecer la base del juego. Se especificó la estética (estilo Roblox, bloque azul con ojos) para que la IA generara código con identidad visual clara desde el principio, no un personaje genérico.

---

### PROMPT 2 – Mejora de la física y doble salto

**Qué se pidió:**
> "Agrega doble salto al jugador. El primer salto es desde el suelo, el segundo en el aire. Una vez que toca una plataforma, los saltos se recargan. También añade una constante MAX_SALTOS = 2 para que sea fácil modificarlo."

**Por qué se ajustó el prompt:**
El primer intento generaba un salto infinito (podías saltar siempre en el aire). Se refinó el prompt especificando que los saltos deben **recargarse solo al tocar suelo o plataforma**, y se pidió una constante nombrada para facilitar futuros ajustes.

---

### PROMPT 3 – Sistema de niveles y pantalla de victoria

**Qué se pidió:**
> "Añade un sistema de 3 niveles. Cada nivel tiene sus propias plataformas y posición inicial del jugador. Cuando el jugador toca la meta (estrella dorada), pasa al siguiente nivel. Si completa todos, muestra una pantalla de victoria total con overlay semitransparente."

**Por qué se ajustó el prompt:**
Primero se pidió solo "pantallas de nivel" sin especificar el overlay. El resultado fue texto simple sin fondo. Se refinó pidiendo explícitamente un **panel semitransparente con borde de color** para que visualmente se parezca más a los menús de Roblox.

---

## 🔁 Iteración y Mejoras

### Mejora 1 – Personaje con cara
El personaje inicial era un rectángulo azul liso. Se pidió a la IA que dibujara **ojos con pupila** y que el personaje **mirara en la dirección de movimiento**, lo cual implicó regenerar la imagen del sprite cada vez que cambia de dirección.

### Mejora 2 – Nubes animadas en el fondo
El fondo era un color sólido. Se solicitó un **gradiente de cielo con nubes que se mueven lentamente**, añadiendo profundidad visual sin afectar el rendimiento.

### Mejora 3 – Efecto de brillo en la meta
La meta era un rectángulo estático. Se añadió un **efecto de rebote/brillo parpadeante** basado en `pygame.time.get_ticks()` para hacerla más llamativa y fácil de localizar.

---

## ✅ Validación del resultado

### Cómo se probó:
- Se ejecutó el juego en cada nivel para verificar que las plataformas estuvieran ubicadas correctamente y fueran alcanzables.
- Se probó caer al vacío para confirmar que aparece la pantalla de "CAÍSTE".
- Se verificó que el doble salto funciona y se recarga al tocar suelo.
- Se probó el flujo completo: Nivel 1 → 2 → 3 → victoria total → reinicio.

### Errores y ajustes encontrados:
| Problema | Causa | Solución |
|----------|-------|----------|
| El jugador atravesaba plataformas a alta velocidad | La velocidad vertical superaba el alto de las plataformas en un solo frame | Se limitó `vel_y` a 20 como máximo |
| Doble salto infinito en el aire | Condición de "en suelo" no se reseteaba correctamente | Se cambió a resetear `saltos_restantes` solo en colisión vertical positiva |
| La meta no se veía en nivel 3 | Coordenadas fuera de pantalla | Se ajustaron las coordenadas revisando el diseño del nivel |

---

## 💬 Reflexión Final

### ¿Qué aprendí usando IA para programar?
Aprendí que la IA es muy eficiente para generar código de estructura repetitiva (como múltiples niveles o efectos visuales), pero que los **detalles de comportamiento** (como cuándo recargar el salto o cómo manejar colisiones) requieren que yo entienda la lógica para poder corregir los errores.

### ¿Ventajas del vibecoding?
- Velocidad: en minutos tenía una base funcional que tomaría horas construir desde cero.
- Aprendizaje activo: al leer el código generado, entendí conceptos como sprites, colisión AABB y game loops.
- Iteración rápida: cambiar la estética o agregar mecánicas fue tan sencillo como describir qué quería.

### ¿Límites del vibecoding?
- La IA a veces genera código que "parece correcto" pero tiene bugs sutiles (como el salto infinito).
- Sin entender el código, no puedo depurarlo ni extenderlo con confianza.
- Los prompts vagos producen resultados genéricos; los prompts precisos producen resultados específicos.

### ¿Qué partes comprendo y cuáles necesito reforzar?
| Comprendo | Necesito reforzar |
|-----------|-------------------|
| Game loop (eventos → actualizar → dibujar) | Optimización de colisiones para muchos objetos |
| Gravedad y velocidad acumulativa | Animaciones por spritesheet |
| Sistema de estados (jugando/muerto/ganaste) | Uso avanzado de `pygame.sprite.Group` |
| Herencia de clases con `pygame.sprite.Sprite` | Añadir sonido con `pygame.mixer` |

---

## 🛠️ Herramientas usadas
- **Lenguaje:** Python 3.x
- **Librería:** Pygame
- **IA de apoyo:** Claude (Anthropic)
- **Editor:** VS Code
