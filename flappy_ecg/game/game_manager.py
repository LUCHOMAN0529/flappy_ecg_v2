import pygame
import time
import config as cfg

from game.bird       import Bird
from game.pipes      import Pipe
from game.background import Background
from game.heart_widget import HeartWidget
from game.score_manager import ScoreManager
from game.screens    import IntroScreen, GameOverScreen


def _load_sound(path):
    import os
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            print(f"[Aviso] No se pudo cargar sonido: {path}")
    return None


def _play(sound):
    if sound:
        sound.play()


# -----------------------------------------------------------------------

class GameManager:

    # --- Estados del juego ---
    STATE_INTRO     = "intro"
    STATE_PLAYING   = "playing"
    STATE_DYING     = "dying"       # animación breve de muerte antes del game over
    STATE_GAME_OVER = "game_over"

    DEATH_ANIM_DURATION = 1.2       # segundos de animación de caída

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy ECG")
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont("Arial", 30, bold=True)

        # Sonidos
        self.snd_jump      = _load_sound("sounds/jump.wav")
        self.snd_score     = _load_sound("sounds/score.wav")
        self.snd_game_over = _load_sound("sounds/game_over.wav")

        # Módulos persistentes
        self.score_manager = ScoreManager()
        self.intro_screen  = IntroScreen()
        self.go_screen     = GameOverScreen()

        # Bandera de Arduino (se actualiza desde main.py)
        self.arduino_connected = False

        self._state = self.STATE_INTRO
        self._state_timer = 0.0        # tiempo acumulado en el estado actual

        self._reset_gameplay()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    def _reset_gameplay(self):
        self.bird       = Bird()
        self.pipes      = []
        self.background = Background()
        self.score      = 0
        self.total_beats = 0
        self.last_pipe_time = pygame.time.get_ticks()

        # Corazón en pantalla (esquina superior derecha)
        self.heart = HeartWidget(cfg.SCREEN_WIDTH - 60, 40, base_size=20)

        self._prev_time = time.time()

    # ------------------------------------------------------------------
    # API pública para main.py
    # ------------------------------------------------------------------
    def set_arduino_connected(self, connected: bool):
        self.arduino_connected = connected

    def ecg_jump(self):
        """Llamado por el detector de picos R."""
        now_ms = int(time.time() * 1000)
        self.heart.beat(now_ms)

        if self._state == self.STATE_PLAYING:
            self.bird.jump()
            self.total_beats += 1
            _play(self.snd_jump)

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    if self._state == self.STATE_PLAYING:
                        self.bird.jump()
                        self.total_beats += 1
                        self.heart.beat(int(time.time() * 1000))
                        _play(self.snd_jump)
        return True

    def update(self):
        now = time.time()
        dt  = now - self._prev_time
        self._prev_time = now

        self._state_timer += dt
        self.heart.update(dt)

        if self._state == self.STATE_INTRO:
            self._update_intro(dt)

        elif self._state == self.STATE_PLAYING:
            self._update_playing(dt)

        elif self._state == self.STATE_DYING:
            self._update_dying(dt)

        elif self._state == self.STATE_GAME_OVER:
            self._update_game_over()

    def draw(self):
        if self._state == self.STATE_INTRO:
            self.intro_screen.draw(self.screen, self.arduino_connected)

        else:
            # Fondo + tuberías + pájaro siempre visibles
            self.background.update()
            self.background.draw(self.screen)
            for pipe in self.pipes:
                pipe.draw(self.screen)
            self.bird.draw(self.screen)

            # HUD: puntuación + corazón
            self._draw_hud()

            if self._state == self.STATE_GAME_OVER:
                self.go_screen.draw(
                    self.screen,
                    score          = self.score,
                    high_score     = self.score_manager.high_score,
                    last_score     = self.score_manager.last_score,
                    total_beats    = self.total_beats,
                    time_remaining = cfg.GAME_OVER_WAIT_SECONDS - self._state_timer,
                )

        pygame.display.flip()

    def tick(self):
        self.clock.tick(cfg.FPS)

    # ------------------------------------------------------------------
    # Estados internos
    # ------------------------------------------------------------------
    def _update_intro(self, dt: float):
        done = self.intro_screen.update(dt, self.arduino_connected)
        if done:
            self._change_state(self.STATE_PLAYING)

    def _update_playing(self, dt: float):
        self.bird.update(dt)
        self.background.update()

        now = pygame.time.get_ticks()
        if now - self.last_pipe_time > cfg.PIPE_DISTANCE_MS:
            self.pipes.append(Pipe(cfg.SCREEN_WIDTH))
            self.last_pipe_time = now

        for pipe in self.pipes:
            pipe.update()
            if (self.bird.rect.colliderect(pipe.top_rect) or
                    self.bird.rect.colliderect(pipe.bottom_rect)):
                self._trigger_death()
                return
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                _play(self.snd_score)

        if self.bird.y > cfg.SCREEN_HEIGHT or self.bird.y < 0:
            self._trigger_death()
            return

        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

    def _update_dying(self, dt: float):
        """Animación de caída antes de mostrar game over."""
        self.bird.update(dt)
        if self._state_timer >= self.DEATH_ANIM_DURATION:
            self._change_state(self.STATE_GAME_OVER)
            self.score_manager.register_game(self.score)

    def _update_game_over(self):
        if self._state_timer >= cfg.GAME_OVER_WAIT_SECONDS:
            self._change_state(self.STATE_PLAYING)
            self._reset_gameplay()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _trigger_death(self):
        self.bird.kill()
        _play(self.snd_game_over)
        self._change_state(self.STATE_DYING)

    def _change_state(self, new_state: str):
        self._state       = new_state
        self._state_timer = 0.0

    def _draw_hud(self):
        # Puntuación
        score_surf = self.font.render(f"Puntuación: {self.score}", True, cfg.COLOR_WHITE)
        self.screen.blit(score_surf, (10, 10))

        # High score
        hs_font = pygame.font.SysFont("Arial", 20)
        hs_surf = hs_font.render(f"Récord: {self.score_manager.high_score}", True, cfg.COLOR_GOLD)
        self.screen.blit(hs_surf, (10, 44))

        # Corazón pulsante + BPM
        self.heart.draw(self.screen)