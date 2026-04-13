import pygame
import os
import config as cfg


class Background:
    def __init__(self):
        self.ground_x = 0
        self.ground_speed = 3
        self.ground_height = 50
        self.ground_y = cfg.SCREEN_HEIGHT - self.ground_height

        bg_path = os.path.join(os.path.dirname(__file__), "..", "images", "background.png")
        if os.path.exists(bg_path):
            self.bg_image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
            self.use_bg_image = True
        else:
            self.bg_image = None
            self.use_bg_image = False

        ground_path = os.path.join(os.path.dirname(__file__), "..", "images", "ground.png")
        if os.path.exists(ground_path):
            self.ground_image = pygame.image.load(ground_path).convert()
            self.ground_image = pygame.transform.scale(self.ground_image, (cfg.SCREEN_WIDTH, self.ground_height))
            self.use_ground_image = True
        else:
            self.ground_image = None
            self.use_ground_image = False

    def update(self):
        self.ground_x -= self.ground_speed
        if self.ground_x <= -cfg.SCREEN_WIDTH:
            self.ground_x = 0

    def draw(self, surface: pygame.Surface):
        if self.use_bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(cfg.COLOR_SKY_BLUE)

        if self.use_ground_image:
            surface.blit(self.ground_image, (self.ground_x, self.ground_y))
            surface.blit(self.ground_image, (self.ground_x + cfg.SCREEN_WIDTH, self.ground_y))
        else:
            pygame.draw.rect(surface, cfg.COLOR_GROUND_ARENA,
                             pygame.Rect(self.ground_x, self.ground_y, cfg.SCREEN_WIDTH, self.ground_height))
            pygame.draw.rect(surface, cfg.COLOR_GROUND_ARENA,
                             pygame.Rect(self.ground_x + cfg.SCREEN_WIDTH, self.ground_y, cfg.SCREEN_WIDTH, self.ground_height))
            pygame.draw.line(surface, cfg.COLOR_GREEN_PIPE,
                             (self.ground_x, self.ground_y),
                             (self.ground_x + cfg.SCREEN_WIDTH * 2, self.ground_y), 4)
