import pygame
import config as cfg
from game.heart_widget import HeartWidget


def _overlay(surface, alpha=160):
    ov = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    surface.blit(ov, (0, 0))


def _centered_text(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    surface.blit(rendered, (cfg.SCREEN_WIDTH // 2 - rendered.get_width() // 2, y))
    return rendered.get_height()


# -----------------------------------------------------------------------
# PANTALLA DE INICIO
# -----------------------------------------------------------------------
class IntroScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont("Arial", 56, bold=True)
        self.font_sub   = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.heart      = HeartWidget(cfg.SCREEN_WIDTH // 2, 260, base_size=36)
        self._timer      = 0.0
        self._beat_timer = 0.0

    def update(self, dt: float, arduino_connected: bool) -> bool:
        self._timer      += dt
        self._beat_timer += dt
        if self._beat_timer >= 0.8:
            self._beat_timer = 0.0
            self.heart.beat(int(self._timer * 1000))
        self.heart.update(dt)
        if arduino_connected and self._timer >= 1.0:
            return True
        if not arduino_connected and self._timer >= 3.0:
            return True
        return False

    def draw(self, surface: pygame.Surface, arduino_connected: bool):
        surface.fill(cfg.COLOR_SKY_BLUE)
        _overlay(surface, 100)
        _centered_text(surface, "FLAPPY  ECG", self.font_title, cfg.COLOR_WHITE, 80)
        _centered_text(surface, "Controla el pájaro con tu corazón",
                       self.font_sub, cfg.COLOR_HEART_PINK, 155)
        self.heart.draw(surface)
        if arduino_connected:
            msg   = "Arduino conectado — iniciando..."
            color = cfg.COLOR_GREEN_OK
        else:
            msg   = "Modo teclado (ESPACIO para saltar)"
            color = cfg.COLOR_GRAY
        _centered_text(surface, msg, self.font_small, color, 340)


# -----------------------------------------------------------------------
# PANTALLA DE GAME OVER
# -----------------------------------------------------------------------
_MESSAGES = [
    (0,  "¡Mejor suerte la próxima!"),
    (3,  "¡Buen intento!"),
    (7,  "¡Nada mal!"),
    (12, "¡Muy bien!"),
    (20, "¡Increíble!"),
    (35, "¡Eres un maestro!"),
]

def _get_message(score: int) -> str:
    msg = _MESSAGES[0][1]
    for threshold, text in _MESSAGES:
        if score >= threshold:
            msg = text
    return msg


class GameOverScreen:
    def __init__(self):
        self.font_big    = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_mid    = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_normal = pygame.font.SysFont("Arial", 22)
        self.font_small  = pygame.font.SysFont("Arial", 18)

    def draw(self, surface: pygame.Surface,
             score: int, high_score: int,
             last_score, total_beats: int,
             time_remaining: float):

        _overlay(surface, 175)

        y = 70

        # Título
        _centered_text(surface, "JUEGO TERMINADO", self.font_big, cfg.COLOR_RED_ERROR, y)
        y += 65

        # Mensaje dinámico
        _centered_text(surface, _get_message(score), self.font_normal, cfg.COLOR_WHITE, y)
        y += 45

        # Puntuación actual
        new_record = score > 0 and score >= high_score
        score_color = cfg.COLOR_GOLD if new_record else cfg.COLOR_WHITE
        label = "¡NUEVO RÉCORD!   " if new_record else ""
        _centered_text(surface, f"{label}Puntuación: {score}", self.font_mid, score_color, y)
        y += 42

        # High score
        _centered_text(surface, f"High Score: {high_score}", self.font_normal, cfg.COLOR_GOLD, y)
        y += 38

        # Último puntaje (partida anterior), solo si existe y es distinta a la actual
        if last_score is not None and last_score != score:
            _centered_text(surface, f"Última partida: {last_score} pts",
                           self.font_normal, cfg.COLOR_GRAY, y)
            y += 38

        # Latidos totales
        _centered_text(surface, f"Saltos en esta partida: {total_beats}",
                       self.font_normal, cfg.COLOR_HEART_PINK, y)
        y += 45

        # Cuenta regresiva
        secs = max(0, int(time_remaining) + 1)
        _centered_text(surface, f"Reiniciando en {secs}...",
                       self.font_small, cfg.COLOR_GRAY, y)
