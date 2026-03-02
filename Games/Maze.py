#--- Manthan Vinzuda ---
import pygame
import random
import sys
from collections import deque

# --- Configuration & Colors ---
BG_COLOR = (30, 30, 46)       # Dark purple/gray background
WALL_COLOR = (137, 180, 250)  # Soft blue for walls
PLAYER_COLOR = (243, 139, 168) # Neon pink/red for the player
GOAL_COLOR = (166, 227, 161)   # Neon green for the goal
PATH_COLOR = (249, 226, 175)   # Neon yellow for the solver path
TEXT_COLOR = (205, 214, 244)   # White/gray text

# --- BIG PUZZLE SETTINGS ---
WIDTH = 1200
COLS, ROWS = 60, 40
CELL_SIZE = WIDTH // COLS
HEIGHT = ROWS * CELL_SIZE 
FPS = 60

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self, surface):
        x = self.x * CELL_SIZE
        y = self.y * CELL_SIZE
        line_width = 2

        if self.walls['top']:
            pygame.draw.line(surface, WALL_COLOR, (x, y), (x + CELL_SIZE, y), line_width)
        if self.walls['right']:
            pygame.draw.line(surface, WALL_COLOR, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), line_width)
        if self.walls['bottom']:
            pygame.draw.line(surface, WALL_COLOR, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), line_width)
        if self.walls['left']:
            pygame.draw.line(surface, WALL_COLOR, (x, y + CELL_SIZE), (x, y), line_width)

def generate_maze():
    grid = [[Cell(x, y) for y in range(ROWS)] for x in range(COLS)]
    stack = []
    
    current = grid[0][0]
    current.visited = True
    
    def get_unvisited_neighbors(cell):
        neighbors = []
        x, y = cell.x, cell.y
        if y > 0 and not grid[x][y-1].visited: neighbors.append(('top', grid[x][y-1]))
        if x < COLS - 1 and not grid[x+1][y].visited: neighbors.append(('right', grid[x+1][y]))
        if y < ROWS - 1 and not grid[x][y+1].visited: neighbors.append(('bottom', grid[x][y+1]))
        if x > 0 and not grid[x-1][y].visited: neighbors.append(('left', grid[x-1][y]))
        return neighbors

    completed = False
    while not completed:
        neighbors = get_unvisited_neighbors(current)
        if neighbors:
            direction, next_cell = random.choice(neighbors)
            stack.append(current)
            
            if direction == 'top':
                current.walls['top'] = False
                next_cell.walls['bottom'] = False
            elif direction == 'right':
                current.walls['right'] = False
                next_cell.walls['left'] = False
            elif direction == 'bottom':
                current.walls['bottom'] = False
                next_cell.walls['top'] = False
            elif direction == 'left':
                current.walls['left'] = False
                next_cell.walls['right'] = False
                
            current = next_cell
            current.visited = True
        elif stack:
            current = stack.pop()
        else:
            completed = True
            
    return grid

def solve_maze(grid, start_x, start_y, goal_x, goal_y):
    """Solves the maze using Breadth-First Search (BFS) to find the shortest path."""
    queue = deque([[(start_x, start_y)]])
    visited = set()
    visited.add((start_x, start_y))

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        if x == goal_x and y == goal_y:
            return path

        current_cell = grid[x][y]
        
        # Check all possible moves from current cell (where there are no walls)
        moves = []
        if not current_cell.walls['top']: moves.append((x, y - 1))
        if not current_cell.walls['bottom']: moves.append((x, y + 1))
        if not current_cell.walls['left']: moves.append((x - 1, y))
        if not current_cell.walls['right']: moves.append((x + 1, y))

        for next_x, next_y in moves:
            if (next_x, next_y) not in visited:
                visited.add((next_x, next_y))
                new_path = list(path)
                new_path.append((next_x, next_y))
                queue.append(new_path)
                
    return []

def draw_glow(surface, color, pos, radius):
    x, y = pos
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))
        glow_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 50), (r, r), r)
        surface.blit(glow_surf, (x - r, y - r))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mega Neon Maze + Auto Solver")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Segoe UI", 64, bold=True)
    small_font = pygame.font.SysFont("Segoe UI", 24)

    grid = generate_maze()
    
    player_x, player_y = 0, 0
    goal_x, goal_y = COLS - 1, ROWS - 1
    
    game_over = False
    solved_path = [] # Stores the auto-solver path

    running = True
    while running:
        screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and not game_over:
                current_cell = grid[player_x][player_y]
                moved = False
                
                # Normal Movement
                if event.key == pygame.K_UP and not current_cell.walls['top']:
                    player_y -= 1; moved = True
                elif event.key == pygame.K_DOWN and not current_cell.walls['bottom']:
                    player_y += 1; moved = True
                elif event.key == pygame.K_LEFT and not current_cell.walls['left']:
                    player_x -= 1; moved = True
                elif event.key == pygame.K_RIGHT and not current_cell.walls['right']:
                    player_x += 1; moved = True
                    
                # Auto Solver Trigger
                elif event.key == pygame.K_s:
                    solved_path = solve_maze(grid, player_x, player_y, goal_x, goal_y)

                # Clear path if player moves manually
                if moved:
                    solved_path = []

            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    grid = generate_maze()
                    player_x, player_y = 0, 0
                    solved_path = []
                    game_over = False

        if player_x == goal_x and player_y == goal_y:
            game_over = True

        # Draw Maze Walls
        for x in range(COLS):
            for y in range(ROWS):
                grid[x][y].draw(screen)

        # Draw Solved Path (If triggered)
        if len(solved_path) > 1:
            for i in range(len(solved_path) - 1):
                p1_x = solved_path[i][0] * CELL_SIZE + CELL_SIZE // 2
                p1_y = solved_path[i][1] * CELL_SIZE + CELL_SIZE // 2
                p2_x = solved_path[i+1][0] * CELL_SIZE + CELL_SIZE // 2
                p2_y = solved_path[i+1][1] * CELL_SIZE + CELL_SIZE // 2
                
                # Draw a glowing thick line for the path
                pygame.draw.line(screen, PATH_COLOR, (p1_x, p1_y), (p2_x, p2_y), 4)
                pygame.draw.circle(screen, PATH_COLOR, (p1_x, p1_y), 3)

        # Draw Goal
        gx_center = goal_x * CELL_SIZE + CELL_SIZE // 2
        gy_center = goal_y * CELL_SIZE + CELL_SIZE // 2
        draw_glow(screen, GOAL_COLOR, (gx_center, gy_center), CELL_SIZE // 2 - 1)
        pygame.draw.circle(screen, GOAL_COLOR, (gx_center, gy_center), max(2, CELL_SIZE // 4))

        # Draw Player
        px_center = player_x * CELL_SIZE + CELL_SIZE // 2
        py_center = player_y * CELL_SIZE + CELL_SIZE // 2
        draw_glow(screen, PLAYER_COLOR, (px_center, py_center), CELL_SIZE // 2 - 1)
        pygame.draw.circle(screen, PLAYER_COLOR, (px_center, py_center), max(2, CELL_SIZE // 4))

        # UI Instructions
        if not game_over:
            instruct_text = small_font.render("Press 'S' for Auto-Solve  |  Arrow Keys to Move", True, TEXT_COLOR)
            screen.blit(instruct_text, (10, HEIGHT - 35))

        # Draw Game Over Text
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            text = font.render("YOU WIN! Press SPACE to replay", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
