
# effects.py
import pygame
import random
from settings import *

class Particle:
    def __init__(self, x, y, color, speed, lifetime, size):
        self.x, self.y = x, y
        self.dx, self.dy = speed
        self.color = color
        self.lifetime = lifetime
        self.max_life = lifetime
        self.size = size

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int((self.lifetime / self.max_life) * 255)
            # Create a temporary surface for alpha
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

class EffectManager:
    def __init__(self):
        self.particles = []

    def spawn_ambient(self):
        if random.random() < 0.1: # Spawn rate
            x = random.randint(0, WINDOW_WIDTH)
            y = WINDOW_HEIGHT + 20
            self.particles.append(Particle(x, y, (255, 255, 255), (random.uniform(-0.5, 0.5), random.uniform(-1, -2)), random.randint(200, 400), random.randint(1, 3)))

    def spawn_confetti(self, x, y):
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]
        for _ in range(50):
            self.particles.append(Particle(x, y, random.choice(colors), (random.uniform(-4, 4), random.uniform(-4, 4)), random.randint(60, 120), random.randint(3, 6)))

    def update_and_draw(self, surface):
        self.spawn_ambient()
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)
            else:
                p.draw(surface)
