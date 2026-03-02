#-- Manthann Vinzuda --
import pygame
import sys
import random

# --- Initialize Pygame ---
pygame.init()
pygame.font.init()

# --- Configuration & Styling ---
WIDTH, HEIGHT = 900, 600
FPS = 60

# Neon Color Palette
BG_COLOR = (18, 18, 20)          # Dark grey/black
PLAYER1_COLOR = (0, 229, 255)    # Neon Cyan
PLAYER2_COLOR = (255, 0, 127)    # Neon Pink
BALL_COLOR = (255, 255, 255)     # White
LINE_COLOR = (50, 50, 50)        # Dim grey for center line

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis")
clock = pygame.time.Clock()
font = pygame.font.SysFont("impact", 50)

# --- Game Objects ---
class Paddle:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 15, 100)
        self.color = color
        self.speed = 8

    def draw(self):
        # Draw main paddle
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        # Fake glow effect (draw slightly larger, transparent rects - simplified here with borders)
        pygame.draw.rect(screen, self.color, self.rect.inflate(4, 4), 2, border_radius=5)

    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= self.speed

    def move_down(self):
        if self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 10, HEIGHT//2 - 10, 20, 20)
        self.base_speed = 6
        self.speed_x = self.base_speed * random.choice([1, -1])
        self.speed_y = self.base_speed * random.choice([1, -1])
        self.trail = [] # Store previous positions for animation

    def draw(self):
        # Draw Trail Animation
        for i, pos in enumerate(self.trail):
            # Calculate trail size and fake opacity
            radius = int(10 * (i / len(self.trail)))
            if radius > 0:
                pygame.draw.circle(screen, (100, 100, 100), (pos[0] + 10, pos[1] + 10), radius)

        # Draw actual ball
        pygame.draw.circle(screen, BALL_COLOR, self.rect.center, 10)

    def move(self):
        # Record position for trail
        self.trail.append((self.rect.x, self.rect.y))
        if len(self.trail) > 15: # Keep trail length limited
            self.trail.pop(0)

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1
            # Add a slight random variance to make it unpredictable
            self.speed_y += random.uniform(-0.5, 0.5) 

    def reset(self):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        self.speed_x = self.base_speed * random.choice([1, -1])
        self.speed_y = self.base_speed * random.choice([1, -1])
        self.trail.clear()

# --- Initialize Entities ---
player1 = Paddle(30, HEIGHT//2 - 50, PLAYER1_COLOR)
player2 = Paddle(WIDTH - 45, HEIGHT//2 - 50, PLAYER2_COLOR)
ball = Ball()

score1 = 0
score2 = 0

def draw_center_line():
    for y in range(0, HEIGHT, 30):
        if y % 60 == 0:
            pygame.draw.rect(screen, LINE_COLOR, (WIDTH//2 - 2, y, 4, 30))

# --- Main Game Loop ---
running = True
while running:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    # 2. Get Key Presses
    keys = pygame.key.get_pressed()
    
    # Player 1 Controls (W and S)
    if keys[pygame.K_w]:
        player1.move_up()
    if keys[pygame.K_s]:
        player1.move_down()
        
    # Player 2 Controls (Up and Down Arrows)
    if keys[pygame.K_UP]:
        player2.move_up()
    if keys[pygame.K_DOWN]:
        player2.move_down()

    # 3. Update Game Logic
    ball.move()

    # Collision with Paddles
    if ball.rect.colliderect(player1.rect) and ball.speed_x < 0:
        ball.speed_x *= -1.1 # Reverse direction and increase speed by 10%
        # Adjust Y speed based on where it hit the paddle for realistic control
        offset = (ball.rect.centery - player1.rect.centery) / 10
        ball.speed_y += offset

    if ball.rect.colliderect(player2.rect) and ball.speed_x > 0:
        ball.speed_x *= -1.1 
        offset = (ball.rect.centery - player2.rect.centery) / 10
        ball.speed_y += offset

    # Scoring
    if ball.rect.left <= 0:
        score2 += 1
        ball.reset()
    if ball.rect.right >= WIDTH:
        score1 += 1
        ball.reset()

    # Prevent ball from getting too fast
    if ball.speed_x > 15: ball.speed_x = 15
    if ball.speed_x < -15: ball.speed_x = -15

    # 4. Draw Everything
    screen.fill(BG_COLOR)
    
    draw_center_line()
    
    player1.draw()
    player2.draw()
    ball.draw()

    # Draw Scores
    score_text1 = font.render(str(score1), True, PLAYER1_COLOR)
    score_text2 = font.render(str(score2), True, PLAYER2_COLOR)
    screen.blit(score_text1, (WIDTH//4, 30))
    screen.blit(score_text2, (WIDTH - WIDTH//4, 30))

    # 5. Update Display and Tick Clock
    pygame.display.flip()
    clock.tick(FPS)
