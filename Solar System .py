                                                                                                                                                     # Created By Manthan Vinzuda....
import pygame
import math
import random

# --- Configuration & Constants ---
WIDTH, HEIGHT = 1000, 800
FPS = 60
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
BLUE = (50, 150, 255)
RED = (200, 50, 50)
GREY = (150, 150, 150)
ORANGE = (255, 140, 0)
SATURN_RING = (180, 160, 140)
SPACE_BLACK = (5, 5, 15)

# --- Classes ---

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.blink_speed = random.uniform(0.02, 0.05)
        self.alpha = random.randint(100, 255)

    def draw(self, screen):
        # Simple blinking effect
        self.alpha += self.blink_speed
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        val = int(155 + 100 * math.sin(pygame.time.get_ticks() * self.blink_speed))
        pygame.draw.circle(s, (val, val, val), (self.size, self.size), self.size)
        screen.blit(s, (self.x, self.y))

class Planet:
    def __init__(self, name, radius, distance, speed, color, has_rings=False):
        self.name = name
        self.radius = radius
        self.distance = distance
        self.speed = speed  # Angular velocity
        self.color = color
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_rings = has_rings
        self.x = 0
        self.y = 0

    def update(self, speed_multiplier):
        self.angle += self.speed * speed_multiplier
        # Trigonometric positioning: 
        # $x = center + distance \cdot \cos(\theta)$
        # $y = center + distance \cdot \sin(\theta)$
        self.x = WIDTH // 2 + math.cos(self.angle) * self.distance
        self.y = HEIGHT // 2 + math.sin(self.angle) * self.distance

    def draw(self, screen, zoom):
        dist = self.distance * zoom
        rad = max(2, int(self.radius * zoom))
        px = WIDTH // 2 + math.cos(self.angle) * dist
        py = HEIGHT // 2 + math.sin(self.angle) * dist

        # Draw Orbit Path
        pygame.draw.circle(screen, (50, 50, 50), (WIDTH // 2, HEIGHT // 2), int(dist), 1)
        
        # Draw Planet
        pygame.draw.circle(screen, self.color, (int(px), int(py)), rad)

        # Saturn's Rings
        if self.has_rings:
            pygame.draw.ellipse(screen, SATURN_RING, (int(px - rad*2), int(py - rad/2), rad*4, rad), 2)

class Moon(Planet):
    def __init__(self, parent_planet, radius, distance, speed, color):
        super().__init__("Moon", radius, distance, speed, color)
        self.parent = parent_planet

    def update(self, speed_multiplier):
        self.angle += self.speed * speed_multiplier
        self.x = self.parent.x + math.cos(self.angle) * self.distance
        self.y = self.parent.y + math.sin(self.angle) * self.distance

    def draw(self, screen, zoom):
        # Calculate position relative to parent
        dist = self.distance * zoom
        px = self.parent.x + (self.x - self.parent.x) * zoom
        py = self.parent.y + (self.y - self.parent.y) * zoom
        pygame.draw.circle(screen, self.color, (int(px), int(py)), max(1, int(self.radius * zoom)))

# --- Main Simulation ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Advanced Solar System Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    stars = [Star() for _ in range(150)]
    
    # Planet Data: (Name, Size, Distance from Sun, Speed, Color, Rings?)
    planets = [
        Planet("Mercury", 4, 60, 0.047, GREY),
        Planet("Venus", 7, 90, 0.035, ORANGE),
        Planet("Earth", 8, 130, 0.029, BLUE),
        Planet("Mars", 6, 170, 0.024, RED),
        Planet("Jupiter", 18, 240, 0.013, (200, 160, 100)),
        Planet("Saturn", 15, 320, 0.009, (210, 180, 140), True)
    ]
    
    earth = planets[2]
    moon = Moon(earth, 2, 15, 0.1, (200, 200, 200))

    sim_speed = 1.0
    zoom = 1.0
    paused = False
    running = True

    while running:
        screen.fill(SPACE_BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: paused = not paused
                if event.key == pygame.K_UP: sim_speed += 0.2
                if event.key == pygame.K_DOWN: sim_speed = max(0.2, sim_speed - 0.2)
                if event.key == pygame.K_ESCAPE: running = False
            if event.type == pygame.MOUSEWHEEL:
                zoom += event.y * 0.1
                zoom = max(0.3, min(2.0, zoom))

        # --- Update Logic ---
        if not paused:
            for p in planets:
                p.update(sim_speed)
            moon.update(sim_speed)

        # --- Draw Logic ---
        for s in stars: s.draw(screen)
        
        # Draw Sun (with pulsing effect)
        pulse = 2 * math.sin(pygame.time.get_ticks() * 0.005)
        pygame.draw.circle(screen, YELLOW, (WIDTH // 2, HEIGHT // 2), int((30 + pulse) * zoom))
        
        for p in planets:
            p.draw(screen, zoom)
        moon.draw(screen, zoom)

        # --- UI Panel ---
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        speed_text = font.render(f"Speed: {sim_speed:.1f}x", True, WHITE)
        zoom_text = font.render(f"Zoom: {zoom:.1f}x", True, WHITE)
        screen.blit(fps_text, (10, 10))
        screen.blit(speed_text, (10, 30))
        screen.blit(zoom_text, (10, 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
