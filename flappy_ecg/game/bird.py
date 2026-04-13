import pygame
import math
import os
import config as cfg


class Bird:
    def __init__(self):
        self.x = 100
        self.y = cfg.SCREEN_HEIGHT // 2
        self.velocity = 0

        self.dead = False
        self.death_rotation = 0

        # Alas
        self._wing_timer = 0.0
        self._wing_flapping = False
        self._wing_duration = 0.4

        self.size = 20
        self.rect = pygame.Rect(self.x - self.size, self.y - self.size,
                                self.size * 2, self.size * 2)

    def jump(self):
        self.velocity = cfg.JUMP_FORCE
        self._wing_flapping = True
        self._wing_timer = 0.0

    def kill(self):
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
        self.rect.centery = int(self.y)
        self.rect.centerx = self.x

        # Alas
        if self._wing_flapping:
            self._wing_timer += dt
            if self._wing_timer >= self._wing_duration:
                self._wing_flapping = False
                self._wing_timer = 0.0

    def draw(self, surface: pygame.Surface):
        cx = self.rect.centerx
        cy = self.rect.centery
        size = self.size

        # Ángulo de rotación por velocidad (o muerte)
        if self.dead:
            angle = self.death_rotation
        else:
            angle = max(-30, min(30, -self.velocity * 3))

        # Ángulo de alas
        if self._wing_flapping:
            wing_angle = math.sin(self._wing_timer * math.pi * 8) * 35
        else:
            wing_angle = 0

        # Dibujar sobre superficie temporal para rotar todo junto
        temp_size = size * 4
        temp = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)
        tcx = temp_size // 2
        tcy = temp_size // 2

        self._draw_wings(temp, tcx, tcy, size, wing_angle)
        self._draw_heart(temp, tcx, tcy, size, cfg.COLOR_HEART_RED)

        # Rotar y blit
        rotated = pygame.transform.rotate(temp, -angle)
        rot_rect = rotated.get_rect(center=(cx, cy))
        surface.blit(rotated, rot_rect)

    @staticmethod
    def _draw_heart(surface, cx, cy, size, color):
        points = []
        for i in range(100):
            t = 2 * math.pi * i / 100
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            scale = size / 17
            points.append((cx + x * scale, cy + y * scale))
        pygame.draw.polygon(surface, color, points)

    @staticmethod
    def _draw_wings(surface, cx, cy, size, angle_deg):
        wing_color = (255, 255, 255)
        wing_w = size * 1.2
        wing_h = size * 0.6

        for side in [-1, 1]:
            base_x = cx + side * size * 0.5
            base_y = cy + size * 0.2

            angle_rad = math.radians(angle_deg * side)
            tip_x = base_x + side * wing_w * math.cos(angle_rad)
            tip_y = base_y - wing_h + wing_w * 0.3 * math.sin(angle_rad)

            points = [
                (base_x, base_y),
                (base_x + side * wing_w * 0.5, base_y - size * 0.6),
                (tip_x, tip_y),
                (base_x + side * wing_w * 0.3, base_y + size * 0.2),
            ]
            pygame.draw.polygon(surface, wing_color, points)
            pygame.draw.polygon(surface, (200, 200, 200), points, 1)