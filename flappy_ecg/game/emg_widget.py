# --- emg_widget.py ---
# Mini gráfica de la señal EMG en tiempo real dentro del juego.
# Muestra la señal cruda, el umbral de activación y marca cada salto.

import pygame
from collections import deque

# Dimensiones del widget
W         = 220
H         = 80
PADDING   = 8
HISTORY   = 100   # cuántas muestras mostrar

# Colores
COL_BG       = (10,  20,  40,  200)   # fondo semitransparente
COL_SIGNAL   = (0,   255, 120)        # señal cruda verde
COL_THRESH   = (255, 80,  80)         # línea de umbral roja
COL_JUMP     = (255, 220, 0)          # destello amarillo en salto
COL_TEXT     = (180, 180, 180)
COL_BORDER   = (60,  80,  120)


class EMGWidget:
    def __init__(self, x: int, y: int, umbral: int = 520):
        self.x       = x
        self.y       = y
        self.umbral  = umbral
        self._data   = deque([0] * HISTORY, maxlen=HISTORY)
        self._jump_flash = 0   # frames de destello al detectar salto
        self._font   = None    # se inicializa en el primer draw (pygame ya está activo)
        self._last_adc = 0

    def push(self, value: int):
        """Agrega una nueva muestra al historial."""
        if value is not None:
            self._last_adc = value
            self._data.append(value)

    def notify_jump(self):
        """Llamar cuando se detecta un salto para mostrar destello."""
        self._jump_flash = 8

    def draw(self, surface: pygame.Surface):
        if self._font is None:
            self._font = pygame.font.SysFont("Arial", 10, bold=True)

        # ── Fondo semitransparente ─────────────────────────────────────
        bg = pygame.Surface((W, H), pygame.SRCALPHA)
        bg.fill(COL_BG)
        surface.blit(bg, (self.x, self.y))
        pygame.draw.rect(surface, COL_BG[:3], (self.x, self.y, W, H), 0)
        pygame.draw.rect(surface, COL_BORDER, (self.x, self.y, W, H), 1)

        # ── Área de gráfica (con margen interno) ──────────────────────
        gx = self.x + PADDING
        gy = self.y + PADDING + 12   # +12 para etiqueta arriba
        gw = W - PADDING * 2
        gh = H - PADDING * 2 - 12

        # Escala: 0-1023 ADC → alto del área
        def to_py(val):
            return gy + gh - int((val / 1023) * gh)

        # Línea de umbral
        thresh_y = to_py(self.umbral)
        pygame.draw.line(surface, COL_THRESH,
                         (gx, thresh_y), (gx + gw, thresh_y), 1)

        # Señal
        data = list(self._data)
        step = gw / max(len(data) - 1, 1)
        pts  = [(int(gx + i * step), to_py(v)) for i, v in enumerate(data)]
        if len(pts) >= 2:
            # Destello amarillo si hubo salto
            color = COL_JUMP if self._jump_flash > 0 else COL_SIGNAL
            pygame.draw.lines(surface, color, False, pts, 1)

        if self._jump_flash > 0:
            self._jump_flash -= 1

        # ── Etiquetas ─────────────────────────────────────────────────
        # Título + ADC actual
        label = self._font.render(
            f"EMG  ADC:{self._last_adc}  umbral:{self.umbral}",
            True, COL_TEXT)
        surface.blit(label, (self.x + PADDING, self.y + 2))

        # Etiqueta del umbral a la derecha
        t_lbl = self._font.render(f"{self.umbral}", True, COL_THRESH)
        surface.blit(t_lbl, (self.x + W - PADDING - t_lbl.get_width(),
                              thresh_y - 10))