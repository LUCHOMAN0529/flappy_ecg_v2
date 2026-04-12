import pygame
import os
import config as cfg


class Bird:
    def __init__(self):
        # Posición inicial
        self.x = 100
        self.y = cfg.SCREEN_HEIGHT // 2
        self.velocity = 0

        # Estado de muerte (animación de caída)
        self.dead = False
        self.death_rotation = 0

        # Cargar imagen si existe
        img_path = os.path.join("images", "bird.png")
        if os.path.exists(img_path):
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.use_image = True
        else:
            self.image = None
            self.use_image = False
            self.color = cfg.COLOR_YELLOW_BIRD

        w, h = (40, 40) if self.use_image else (30, 30)
        self.rect = pygame.Rect(self.x, self.y, w, h)

    def jump(self):
        """Impulsa al pájaro hacia arriba."""
        self.velocity = cfg.JUMP_FORCE

    def kill(self):
        """Marca al pájaro como muerto para la animación."""
        self.dead = True

    def update(self, dt: float):
        if self.dead:
            self.velocity += cfg.GRAVITY_ACCEL * 1.5
            self.death_rotation = min(self.death_rotation + 6, 90)
        else:
            self.velocity += cfg.GRAVITY_ACCEL
            if self.velocity > 10:
                self.velocity = 10

        self.y += self.velocity
        self.rect.y = int(self.y)

    def draw(self, surface: pygame.Surface):
        if self.use_image:
            angle = self.death_rotation if self.dead else max(-30, min(30, -self.velocity * 3))
            rotated = pygame.transform.rotate(self.image, angle)
            rot_rect = rotated.get_rect(center=self.rect.center)
            surface.blit(rotated, rot_rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
