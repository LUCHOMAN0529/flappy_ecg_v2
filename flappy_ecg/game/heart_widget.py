import pygame
import math
import config as cfg


class HeartWidget:
    def __init__(self, x: int, y: int, base_size: int = 18):
        self.x = x
        self.y = y
        self.base_size = base_size

        self._scale = 1.0
        self._pulse_timer = 0.0
        self._is_pulsing = False

        # Alas
        self._wing_timer = 0.0
        self._wing_flapping = False
        self._wing_duration = 0.4   # segundos que duran agitándose

        # BPM
        self._last_beat_ms = 0
        self._bpm = 0

    def beat(self, current_time_ms: int):
        if self._last_beat_ms > 0:
            interval_ms = current_time_ms - self._last_beat_ms
            if 300 < interval_ms < 2000:
                self._bpm = int(60_000 / interval_ms)
        self._last_beat_ms = current_time_ms
        self._is_pulsing = True
        self._pulse_timer = 0.0
        self._scale = 1.45

        # Activar alas
        self._wing_flapping = True
        self._wing_timer = 0.0

    @property
    def bpm(self) -> int:
        return self._bpm

    def update(self, dt: float):
        if self._is_pulsing:
            self._pulse_timer += dt
            t = self._pulse_timer / 0.35
            if t >= 1.0:
                self._scale = 1.0
                self._is_pulsing = False
            else:
                self._scale = 1.0 + 0.45 * math.sin(t * math.pi)

        if self._wing_flapping:
            self._wing_timer += dt
            if self._wing_timer >= self._wing_duration:
                self._wing_flapping = False
                self._wing_timer = 0.0

    def draw(self, surface: pygame.Surface):
        size = int(self.base_size * self._scale)

        # Ángulo de alas basado en timer
        if self._wing_flapping:
            wing_angle = math.sin(self._wing_timer * math.pi * 8) * 35
        else:
            wing_angle = 0

        self._draw_wings(surface, self.x, self.y, size, wing_angle)
        self._draw_heart(surface, self.x, self.y, size, cfg.COLOR_HEART_RED)

        if self._bpm > 0:
            font = pygame.font.SysFont("Arial", 14, bold=True)
            txt = font.render(f"{self._bpm} BPM", True, cfg.COLOR_HEART_RED)
            surface.blit(txt, (self.x - txt.get_width() // 2, self.y + size + 4))

    @staticmethod
    def _draw_heart(surface, cx, cy, size, color):
        """Corazón clásico de amor con curvas bezier."""
        points = []
        for i in range(100):
            t = 2 * math.pi * i / 100
            # Fórmula matemática del corazón
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            scale = size / 17
            points.append((cx + x * scale, cy + y * scale))
        pygame.draw.polygon(surface, color, points)

    @staticmethod
    def _draw_wings(surface, cx, cy, size, angle_deg):
        """Alas a los lados del corazón."""
        wing_color = (255, 255, 255)
        wing_w = size * 1.2
        wing_h = size * 0.6

        for side in [-1, 1]:  # -1 izquierda, 1 derecha
            # Base del ala
            base_x = cx + side * size * 0.6
            base_y = cy

            # Puntos del ala (forma elíptica simple)
            angle_rad = math.radians(angle_deg * side)
            tip_x = base_x + side * wing_w * math.cos(angle_rad)
            tip_y = base_y - wing_h + wing_w * 0.3 * math.sin(angle_rad)
            ctrl_y = base_y - wing_h * 0.5

            points = [
                (base_x, base_y),
                (base_x + side * wing_w * 0.5, ctrl_y - size * 0.3),
                (tip_x, tip_y),
                (base_x + side * wing_w * 0.3, base_y + size * 0.2),
            ]
            pygame.draw.polygon(surface, wing_color, points)
            pygame.draw.polygon(surface, (200, 200, 200), points, 1)