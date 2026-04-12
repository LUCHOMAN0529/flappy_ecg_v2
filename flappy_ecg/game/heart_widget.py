import pygame
import math
import config as cfg


class HeartWidget:
    """
    Corazón que pulsa en pantalla sincronizado con los latidos detectados.
    Se dibuja con geometría pygame (sin imagen externa).
    """

    def __init__(self, x: int, y: int, base_size: int = 18):
        self.x = x
        self.y = y
        self.base_size = base_size

        # Estado de pulso
        self._scale = 1.0          # escala actual
        self._pulse_timer = 0.0    # segundos desde el último latido
        self._is_pulsing = False

        # BPM
        self._last_beat_ms = 0
        self._bpm = 0

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def beat(self, current_time_ms: int):
        """Llamar cada vez que se detecta un latido."""
        if self._last_beat_ms > 0:
            interval_ms = current_time_ms - self._last_beat_ms
            if 300 < interval_ms < 2000:          # rango razonable 30-200 bpm
                self._bpm = int(60_000 / interval_ms)
        self._last_beat_ms = current_time_ms
        self._is_pulsing = True
        self._pulse_timer = 0.0
        self._scale = 1.45

    @property
    def bpm(self) -> int:
        return self._bpm

    # ------------------------------------------------------------------
    # Update / Draw
    # ------------------------------------------------------------------
    def update(self, dt: float):
        """dt en segundos."""
        if self._is_pulsing:
            self._pulse_timer += dt
            # Animación de 0.35 s: crece rápido y vuelve suave
            t = self._pulse_timer / 0.35
            if t >= 1.0:
                self._scale = 1.0
                self._is_pulsing = False
            else:
                self._scale = 1.0 + 0.45 * math.sin(t * math.pi)

    def draw(self, surface: pygame.Surface):
        size = int(self.base_size * self._scale)
        self._draw_heart(surface, self.x, self.y, size, cfg.COLOR_HEART_RED)

        # Texto BPM debajo del corazón
        if self._bpm > 0:
            font = pygame.font.SysFont("Arial", 14, bold=True)
            txt = font.render(f"{self._bpm} BPM", True, cfg.COLOR_HEART_RED)
            surface.blit(txt, (self.x - txt.get_width() // 2, self.y + size + 4))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _draw_heart(surface, cx, cy, size, color):
        """Dibuja un corazón centrado en (cx, cy) usando círculos + polígono."""
        r = size // 2
        # Dos círculos superiores
        pygame.draw.circle(surface, color, (cx - r // 2, cy - r // 4), r // 2)
        pygame.draw.circle(surface, color, (cx + r // 2, cy - r // 4), r // 2)
        # Triángulo inferior
        points = [
            (cx - r, cy - r // 4),
            (cx + r, cy - r // 4),
            (cx,     cy + r),
        ]
        pygame.draw.polygon(surface, color, points)
