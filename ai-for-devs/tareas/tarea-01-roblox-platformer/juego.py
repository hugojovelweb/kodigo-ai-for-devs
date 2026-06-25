"""
==============================================
  BLOX JUMP Hugo Jovel - Plataforma Estilo Roblox 2D
  Desarrollado con IA como copiloto (Vibecoding)
==============================================
Controles:
  FLECHA IZQUIERDA / A  -> Mover izquierda
  FLECHA DERECHA  / D  -> Mover derecha
  ESPACIO / FLECHA ARRIBA / W -> Saltar
  R                          -> Reiniciar
  ESC                        -> Salir
"""

import pygame
import sys

# ─────────────────────────────────────────────
#  CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────
ANCHO, ALTO = 900, 600
FPS = 60
TITULO = "BLOX JUMP By Hugo Jovel –  Estilo Roblox 2D"

# Paleta de colores (vibrante estilo Roblox)
COLOR_CIELO        = (135, 206, 250)
COLOR_CIELO_ABAJO  = (180, 230, 255)
COLOR_SUELO        = (80, 200, 80)
COLOR_PLATAFORMA   = (255, 80,  80)   # rojo ladrillo
COLOR_PLAT_BORDE   = (200, 40,  40)
COLOR_JUGADOR      = (0,   162, 232)  # azul Roblox
COLOR_JUGADOR_OJO  = (255, 255, 255)
COLOR_JUGADOR_PUPILA = (30, 30, 30)
COLOR_META         = (255, 215, 0)    # dorado
COLOR_META_BORDE   = (200, 160, 0)
COLOR_UI_BG        = (0, 0, 0, 160)
COLOR_TEXTO        = (255, 255, 255)
COLOR_SOMBRA       = (0, 0, 0, 80)
COLOR_NUBE         = (255, 255, 255)

# Física
GRAVEDAD      = 0.6
FUERZA_SALTO  = -14
VEL_MOVIMIENTO = 5
MAX_SALTOS    = 2   # doble salto permitido

# ─────────────────────────────────────────────
#  NIVELES  (lista de plataformas [x, y, ancho, alto])
#  y posición inicial del jugador y de la meta
# ─────────────────────────────────────────────
NIVELES = [
    {
        "nombre": "Nivel 1 – Inicio",
        "jugador_inicio": (80, 480),
        "meta": (820, 120),
        "plataformas": [
            # Suelo
            [0,   550, 900, 50],
            # Plataformas
            [100, 460, 140, 18],
            [280, 390, 140, 18],
            [460, 320, 140, 18],
            [640, 250, 140, 18],
            [460, 175, 200, 18],
            [660, 120, 200, 18],
        ],
    },
    {
        "nombre": "Nivel 2 – Más alto",
        "jugador_inicio": (50, 480),
        "meta": (840, 60),
        "plataformas": [
            [0,   550, 900, 50],
            [0,   400, 120, 18],
            [180, 340, 100, 18],
            [340, 280, 100, 18],
            [200, 210, 120, 18],
            [380, 150, 120, 18],
            [560, 200, 100, 18],
            [700, 130, 120, 18],
            [560, 70,  200, 18],
            [750, 60,  120, 18],
        ],
    },
    {
        "nombre": "Nivel 3 – Desafío",
        "jugador_inicio": (30, 490),
        "meta": (860, 80),
        "plataformas": [
            [0,   550, 300, 50],
            [50,  450,  80, 18],
            [180, 390,  80, 18],
            [300, 470,  80, 18],
            [420, 390,  80, 18],
            [540, 310,  80, 18],
            [660, 390,  80, 18],
            [780, 310,  80, 18],
            [660, 230,  80, 18],
            [540, 160,  80, 18],
            [660, 90,  220, 18],
        ],
    },
]


# ─────────────────────────────────────────────
#  CLASES
# ─────────────────────────────────────────────

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.ancho  = 40
        self.alto   = 48
        self.image  = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        self._dibujar_personaje(mirando_derecha=True)
        self.rect   = self.image.get_rect(topleft=(x, y))
        self.vel_x  = 0
        self.vel_y  = 0
        self.en_suelo       = False
        self.saltos_restantes = MAX_SALTOS
        self.mirando_derecha  = True
        self.animacion_tick   = 0

    def _dibujar_personaje(self, mirando_derecha=True):
        """Dibuja un personaje cuadrado estilo Roblox."""
        self.image.fill((0, 0, 0, 0))
        w, h = self.ancho, self.alto

        # Cuerpo
        pygame.draw.rect(self.image, COLOR_JUGADOR,      (4, 14, w-8, h-14), border_radius=4)
        pygame.draw.rect(self.image, (0, 100, 180),      (4, 14, w-8, h-14), 2, border_radius=4)

        # Cabeza
        pygame.draw.rect(self.image, COLOR_JUGADOR,      (2, 0,  w-4, 20),   border_radius=6)
        pygame.draw.rect(self.image, (0, 100, 180),      (2, 0,  w-4, 20),   2, border_radius=6)

        # Ojos
        ox = 22 if mirando_derecha else 8
        pygame.draw.circle(self.image, COLOR_JUGADOR_OJO,   (ox,    8), 5)
        pygame.draw.circle(self.image, COLOR_JUGADOR_PUPILA,(ox+1 if mirando_derecha else ox-1, 9), 3)

        # Brazos
        pygame.draw.rect(self.image, (0, 120, 200), (0,  16, 5, 18), border_radius=3)
        pygame.draw.rect(self.image, (0, 120, 200), (w-5, 16, 5, 18), border_radius=3)

        # Piernas
        pygame.draw.rect(self.image, (30, 30, 180), (6,  h-16, 12, 14), border_radius=3)
        pygame.draw.rect(self.image, (30, 30, 180), (w-18, h-16, 12, 14), border_radius=3)

    def manejar_input(self, teclas):
        self.vel_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -VEL_MOVIMIENTO
            if self.mirando_derecha:
                self.mirando_derecha = False
                self._dibujar_personaje(False)
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = VEL_MOVIMIENTO
            if not self.mirando_derecha:
                self.mirando_derecha = True
                self._dibujar_personaje(True)

    def saltar(self):
        if self.saltos_restantes > 0:
            self.vel_y = FUERZA_SALTO
            self.en_suelo = False
            self.saltos_restantes -= 1

    def actualizar(self, plataformas):
        # Gravedad
        self.vel_y += GRAVEDAD
        if self.vel_y > 20:
            self.vel_y = 20

        # Movimiento horizontal
        self.rect.x += self.vel_x
        self._colision_horizontal(plataformas)

        # Movimiento vertical
        self.rect.y += int(self.vel_y)
        self.en_suelo = False
        self._colision_vertical(plataformas)

    def _colision_horizontal(self, plataformas):
        for plat in plataformas:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right

    def _colision_vertical(self, plataformas):
        for plat in plataformas:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.en_suelo = True
                    self.saltos_restantes = MAX_SALTOS
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

    def murio(self):
        return self.rect.top > ALTO + 40


class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto):
        super().__init__()
        self.image = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        # Cuerpo principal
        pygame.draw.rect(self.image, COLOR_PLATAFORMA,  (0, 0, ancho, alto), border_radius=4)
        # Borde superior (brillo)
        pygame.draw.rect(self.image, (255, 130, 130),   (2, 2, ancho-4, 5),  border_radius=2)
        # Borde inferior (sombra)
        pygame.draw.rect(self.image, COLOR_PLAT_BORDE,  (0, 0, ancho, alto), 2, border_radius=4)
        self.rect  = self.image.get_rect(topleft=(x, y))


class Meta(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self._tick = 0
        self.base_image = self._crear_imagen()
        self.image = self.base_image.copy()
        self.rect  = self.image.get_rect(topleft=(x, y))

    def _crear_imagen(self):
        img = pygame.Surface((50, 50), pygame.SRCALPHA)
        # Estrella / bandera dorada
        pygame.draw.rect(img, COLOR_META,        (10, 10, 30, 30), border_radius=8)
        pygame.draw.rect(img, COLOR_META_BORDE,  (10, 10, 30, 30), 3, border_radius=8)
        # Texto CHECK
        fuente = pygame.font.SysFont("Arial", 22, bold=True)
        txt = fuente.render("✓", True, (255, 255, 255))
        img.blit(txt, (13, 10))
        return img

    def actualizar(self):
        self._tick += 1
        # Efecto de rebote
        offset = int(4 * abs(pygame.math.Vector2(0, 1).rotate(self._tick * 3).y))
        self.rect.y += (0 if self._tick % 2 else 0)  # posición fija, solo visual


# ─────────────────────────────────────────────
#  FONDO CON NUBES
# ─────────────────────────────────────────────
class Nube:
    def __init__(self, x, y, escala=1.0):
        self.x, self.y = x, y
        self.vel = 0.3 * escala
        self.escala = escala

    def actualizar(self):
        self.x -= self.vel
        if self.x < -200:
            self.x = ANCHO + 100

    def dibujar(self, surf):
        e = self.escala
        cx, cy = int(self.x), int(self.y)
        pygame.draw.ellipse(surf, COLOR_NUBE, (cx,       cy+10, int(80*e), int(35*e)))
        pygame.draw.ellipse(surf, COLOR_NUBE, (cx+10,    cy,    int(60*e), int(40*e)))
        pygame.draw.ellipse(surf, COLOR_NUBE, (cx+40,    cy+5,  int(70*e), int(35*e)))


# ─────────────────────────────────────────────
#  JUEGO PRINCIPAL
# ─────────────────────────────────────────────
class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()

        self.fuente_grande = pygame.font.SysFont("Arial Rounded MT Bold", 48, bold=True)
        self.fuente_media  = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_chica  = pygame.font.SysFont("Arial", 20)

        self.nubes = [
            Nube(100, 60,  1.2),
            Nube(350, 30,  0.8),
            Nube(600, 80,  1.0),
            Nube(800, 45,  0.7),
        ]

        self.nivel_actual = 0
        self.cargar_nivel(self.nivel_actual)
        self.estado = "jugando"  # jugando | ganaste | muerto | victoria_total

    def cargar_nivel(self, idx):
        datos = NIVELES[idx]
        jx, jy = datos["jugador_inicio"]
        mx, my = datos["meta"]

        self.jugador    = Jugador(jx, jy)
        self.plataformas = [Plataforma(*p) for p in datos["plataformas"]]
        self.meta        = Meta(mx, my)
        self.nombre_nivel = datos["nombre"]
        self.mensaje_tick = 0

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if evento.key == pygame.K_r:
                    self.nivel_actual = 0
                    self.cargar_nivel(0)
                    self.estado = "jugando"
                if self.estado == "jugando":
                    if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        self.jugador.saltar()
                if self.estado in ("ganaste", "muerto", "victoria_total"):
                    if evento.key == pygame.K_RETURN:
                        if self.estado == "ganaste":
                            self.nivel_actual += 1
                            self.cargar_nivel(self.nivel_actual)
                            self.estado = "jugando"
                        else:
                            self.nivel_actual = 0
                            self.cargar_nivel(0)
                            self.estado = "jugando"

    def actualizar(self):
        if self.estado != "jugando":
            return
        teclas = pygame.key.get_pressed()
        self.jugador.manejar_input(teclas)
        self.jugador.actualizar(self.plataformas)
        self.meta.actualizar()
        for nube in self.nubes:
            nube.actualizar()

        # ¿Cayó?
        if self.jugador.murio():
            self.estado = "muerto"

        # ¿Llegó a la meta?
        if self.jugador.rect.colliderect(self.meta.rect):
            if self.nivel_actual >= len(NIVELES) - 1:
                self.estado = "victoria_total"
            else:
                self.estado = "ganaste"

    # ── Dibujo ──────────────────────────────
    def dibujar_fondo(self):
        # Gradiente cielo
        for y in range(ALTO):
            t = y / ALTO
            r = int(135 + (180-135)*t)
            g = int(206 + (230-206)*t)
            b = int(250 + (255-250)*t)
            pygame.draw.line(self.pantalla, (r, g, b), (0, y), (ANCHO, y))
        for nube in self.nubes:
            nube.dibujar(self.pantalla)

    def dibujar_ui(self):
        # Nombre de nivel
        txt = self.fuente_chica.render(self.nombre_nivel, True, (50, 50, 50))
        sombra = self.fuente_chica.render(self.nombre_nivel, True, (200,200,200))
        self.pantalla.blit(sombra, (12, 12))
        self.pantalla.blit(txt,    (10, 10))

        # Saltos restantes
        txt2 = self.fuente_chica.render(f"Saltos: {'◆' * self.jugador.saltos_restantes}{'◇' * (MAX_SALTOS - self.jugador.saltos_restantes)}", True, (50,50,50))
        self.pantalla.blit(txt2, (10, 35))

        # Niveles
        txt3 = self.fuente_chica.render(f"Nivel {self.nivel_actual+1}/{len(NIVELES)}", True, (50,50,50))
        self.pantalla.blit(txt3, (ANCHO - txt3.get_width() - 10, 10))

    def dibujar_overlay(self, titulo, subtitulo, color_titulo=(255,220,50)):
        # Fondo semitransparente
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.pantalla.blit(overlay, (0, 0))

        # Panel central
        panel = pygame.Surface((520, 200), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30, 30, 30, 210), (0, 0, 520, 200), border_radius=16)
        pygame.draw.rect(panel, color_titulo,       (0, 0, 520, 200), 3, border_radius=16)
        self.pantalla.blit(panel, (ANCHO//2 - 260, ALTO//2 - 100))

        t1 = self.fuente_grande.render(titulo,    True, color_titulo)
        t2 = self.fuente_media.render(subtitulo,  True, (220, 220, 220))
        self.pantalla.blit(t1, (ANCHO//2 - t1.get_width()//2, ALTO//2 - 80))
        self.pantalla.blit(t2, (ANCHO//2 - t2.get_width()//2, ALTO//2 - 10))

    def dibujar(self):
        self.dibujar_fondo()

        # Plataformas
        for plat in self.plataformas:
            self.pantalla.blit(plat.image, plat.rect)

        # Meta (con efecto de brillo parpadeante)
        tick = pygame.time.get_ticks()
        brillo = abs((tick % 1000) - 500) / 500  # 0..1
        meta_x = self.meta.rect.x + int(3 * brillo)
        meta_y = self.meta.rect.y - int(5 * brillo)
        self.pantalla.blit(self.meta.image, (meta_x, meta_y))

        # Jugador (con sombra)
        sombra_surf = pygame.Surface((self.jugador.ancho, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra_surf, (0, 0, 0, 60), (0, 0, self.jugador.ancho, 8))
        self.pantalla.blit(sombra_surf, (self.jugador.rect.x, self.jugador.rect.bottom - 4))
        self.pantalla.blit(self.jugador.image, self.jugador.rect)

        self.dibujar_ui()

        # Pantallas de estado
        if self.estado == "ganaste":
            self.dibujar_overlay("¡NIVEL SUPERADO!", "Presiona ENTER para continuar →", (100, 255, 100))
        elif self.estado == "muerto":
            self.dibujar_overlay("¡CAÍSTE!", "Presiona ENTER para reintentar  |  R para inicio", (255, 80, 80))
        elif self.estado == "victoria_total":
            self.dibujar_overlay("🏆 ¡GANASTE TODO!", "¡Completaste los 3 niveles!  |  R para reiniciar", (255, 215, 0))

        # Controles (esquina inferior)
        ctrl = self.fuente_chica.render("← → / A D: Mover   |   ESPACIO / W: Saltar   |   R: Reiniciar   |   ESC: Salir", True, (80, 80, 80))
        self.pantalla.blit(ctrl, (ANCHO//2 - ctrl.get_width()//2, ALTO - 24))

        pygame.display.flip()

    def ejecutar(self):
        while True:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)


# ─────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    Juego().ejecutar()
