import pygame
import random
import os
import config as cfg


class Pipe:
    _pipe_image  = None
    _image_loaded = False

    def __init__(self, x):
        self.x = x
        self.width  = cfg.PIPE_WIDTH
        self.gap    = cfg.PIPE_GAP_SIZE
        self.color  = cfg.COLOR_GREEN_PIPE
        self.speed  = 3

        min_height = 50
        max_height = cfg.SCREEN_HEIGHT - self.gap - 50
        self.top_height = random.randint(min_height, max_height)
        self.bottom_y   = self.top_height + self.gap

        self.top_rect    = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width,
                                       cfg.SCREEN_HEIGHT - self.bottom_y)
        self.passed = False

        if not Pipe._image_loaded:
            pipe_path = os.path.join(os.path.dirname(__file__), "..", "images", "pipe.png")
            if os.path.exists(pipe_path):
                Pipe._pipe_image = pygame.image.load(pipe_path).convert_alpha()
            Pipe._image_loaded = True

    def update(self):
        self.x -= self.speed
        self.top_rect.x    = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface: pygame.Surface):
        if Pipe._pipe_image:
            top_img = pygame.transform.scale(Pipe._pipe_image, (self.width, self.top_height))
            top_img = pygame.transform.flip(top_img, False, True)
            surface.blit(top_img, (self.x, 0))
            bottom_h = cfg.SCREEN_HEIGHT - self.bottom_y
            bottom_img = pygame.transform.scale(Pipe._pipe_image, (self.width, bottom_h))
            surface.blit(bottom_img, (self.x, self.bottom_y))
        else:
            pygame.draw.rect(surface, self.color, self.top_rect)
            pygame.draw.rect(surface, self.color, self.bottom_rect)

    def is_off_screen(self):
        return self.x + self.width < 0
