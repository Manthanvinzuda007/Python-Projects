# --- MN --- 
import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()

try:
    font = pygame.font.SysFont('segoeui', 25, bold=True)
    large_font = pygame.font.SysFont('segoeui', 50, bold=True)
except:
    font = pygame.font.Font(pygame.font.get_default_font(), 25)
    large_font = pygame.font.Font(pygame.font.get_default_font(), 50)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

Point = namedtuple('Point', 'x, y')

# Constants
BLOCK_SIZE = 20
FPS = 60  # Game runs at 60 Frames Per Second for zero input delay
BASE_MOVE_DELAY = 120  # Milliseconds between snake movements (lower = faster)

# Premium Color Palette
BG_COLOR = (15, 15, 20)
GRID_COLOR = (25, 25, 35)
SNAKE_HEAD = (0, 255, 128)
SNAKE_BODY = (0, 200, 100)
FOOD_COLOR = (255, 50, 80)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (100, 100, 255)

class NoDelaySnakeGame:
    def __init__(self, width=640, height=480):
        self.w = width
        self.h = height
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Zero-Delay Premium Snake')
        self.clock = pygame.time.Clock()
        
        self.state = GameState.MENU
        self.high_score = 0
        self.reset_game()

    def reset_game(self):
        """Resets the game state."""
        self.current_direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT # Buffers the input
        
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]
        self.score = 0
        self.move_delay = BASE_MOVE_DELAY
        self.last_move_time = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def run(self):
        """Main game loop running at a constant 60 FPS."""
        while True:
            self._handle_events()

            if self.state == GameState.PLAYING:
                current_time = pygame.time.get_ticks()
                
                # Only move the snake when the delay timer finishes
                if current_time - self.last_move_time >= self.move_delay:
                    self.current_direction = self.next_direction
                    self._play_step()
                    self.last_move_time = current_time
                    
            elif self.state == GameState.MENU:
                self._draw_menu("SNAKE", "Press SPACE to Start")
            elif self.state == GameState.GAME_OVER:
                self._draw_menu("GAME OVER", f"Score: {self.score} | Press SPACE to Restart")

            # Always run at 60 FPS for instant input registration
            self.clock.tick(FPS)

    def _handle_events(self):
        """Processes keyboard inputs instantly."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU or self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.PLAYING:
                    # Capture input instantly into next_direction to prevent double-turn suicide bugs
                    if event.key == pygame.K_LEFT and self.current_direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.current_direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                    elif event.key == pygame.K_UP and self.current_direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.current_direction != Direction.UP:
                        self.next_direction = Direction.DOWN

    def _play_step(self):
        self._move(self.current_direction)
        self.snake.insert(0, self.head)

        if self._is_collision():
            if self.score > self.high_score:
                self.high_score = self.score
            self.state = GameState.GAME_OVER
            return

        if self.head == self.food:
            self.score += 1
            # Decrease delay (increase speed) every 5 points, capping at 40ms
            if self.score % 5 == 0 and self.move_delay > 40:
                self.move_delay -= 10
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()

    def _is_collision(self):
        if (self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or 
            self.head.y > self.h - BLOCK_SIZE or self.head.y < 0):
            return True
        if self.head in self.snake[1:]:
            return True
        return False

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT: x += BLOCK_SIZE
        elif direction == Direction.LEFT: x -= BLOCK_SIZE
        elif direction == Direction.DOWN: y += BLOCK_SIZE
        elif direction == Direction.UP: y -= BLOCK_SIZE
        self.head = Point(x, y)

    def _draw_grid(self):
        for x in range(0, self.w, BLOCK_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (x, 0), (x, self.h))
        for y in range(0, self.h, BLOCK_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (0, y), (self.w, y))

    def _update_ui(self):
        self.display.fill(BG_COLOR)
        self._draw_grid()

        for idx, pt in enumerate(self.snake):
            color = SNAKE_HEAD if idx == 0 else SNAKE_BODY
            rect = pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.display, color, rect, border_radius=4)
            
            inner_rect = pygame.Rect(pt.x + 4, pt.y + 4, BLOCK_SIZE - 8, BLOCK_SIZE - 8)
            pygame.draw.rect(self.display, BG_COLOR, inner_rect, border_radius=2)

        center_x = self.food.x + (BLOCK_SIZE // 2)
        center_y = self.food.y + (BLOCK_SIZE // 2)
        pygame.draw.circle(self.display, FOOD_COLOR, (center_x, center_y), BLOCK_SIZE // 2 - 2)

        score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        high_score_text = font.render(f"High Score: {self.high_score}", True, ACCENT_COLOR)
        self.display.blit(score_text, [10, 10])
        self.display.blit(high_score_text, [self.w - high_score_text.get_width() - 10, 10])
        
        pygame.display.flip()

    def _draw_menu(self, title, subtitle):
        self.display.fill(BG_COLOR)
        title_text = large_font.render(title, True, SNAKE_HEAD)
        sub_text = font.render(subtitle, True, TEXT_COLOR)
        
        self.display.blit(title_text, (self.w/2 - title_text.get_width()/2, self.h/2 - 50))
        self.display.blit(sub_text, (self.w/2 - sub_text.get_width()/2, self.h/2 + 20))
        pygame.display.flip()

if __name__ == '__main__':
    game = NoDelaySnakeGame()
    game.run()
