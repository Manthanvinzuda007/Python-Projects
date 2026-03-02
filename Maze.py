                                                                                                                                                      # Created By Manthan Vinzuda....
import pygame
import random
import heapq
import sys

# --- SYSTEM CONSTANTS ---
TILE_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 25, 21  # Must be odd for DFS generation
WIDTH, HEIGHT = GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE
FPS = 30

# COLORS (Material Design Palette)
CLR_WALL = (33, 33, 33)
CLR_PATH = (250, 250, 250)
CLR_PLAYER = (33, 150, 243)
CLR_ENEMY = (244, 67, 54)
CLR_EXIT = (76, 175, 80)
CLR_AI_PATH = (244, 67, 54, 80) # AI logic visualization

class Node:
    """Represents a Graph Node for A* Search"""
    def __init__(self, pos, parent=None, g=0, h=0):
        self.pos = pos
        self.parent = parent
        self.g = g  # Cost from start
        self.h = h  # Heuristic cost to goal
        self.f = g + h # Total cost

    def __lt__(self, other):
        return self.f < other.f

class MazeEngine:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.generate_dfs_maze()
        
    def generate_dfs_maze(self):
        """Recursive Backtracking to create a 'Perfect Maze'"""
        self.grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        def walk(r, c):
            self.grid[r][c] = 0
            dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(dirs)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 < nr < GRID_HEIGHT-1 and 0 < nc < GRID_WIDTH-1 and self.grid[nr][nc] == 1:
                    self.grid[r + dr//2][c + dc//2] = 0
                    walk(nr, nc)

        walk(1, 1)
        # Ensure Exit is reachable
        self.grid[GRID_HEIGHT-2][GRID_WIDTH-2] = 0

    def is_walkable(self, r, c):
        return 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH and self.grid[r][c] == 0

class PathFinder:
    @staticmethod
    def a_star(maze, start, goal):
        """A* Algorithm with Manhattan Heuristic"""
        open_list = []
        heapq.heappush(open_list, Node(start, None, 0, PathFinder.heuristic(start, goal)))
        visited = {} # pos -> g_cost

        while open_list:
            current = heapq.heappop(open_list)

            if current.pos == goal:
                path = []
                while current:
                    path.append(current.pos)
                    current = current.parent
                return path[::-1]

            if current.pos in visited and visited[current.pos] <= current.g:
                continue
            visited[current.pos] = current.g

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current.pos[0] + dr, current.pos[1] + dc)
                if maze.is_walkable(*neighbor):
                    g = current.g + 1
                    h = PathFinder.heuristic(neighbor, goal)
                    heapq.heappush(open_list, Node(neighbor, current, g, h))
        return []

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("B.Tech AI Maze Project")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 20, bold=True)
        
        self.maze = MazeEngine()
        self.player_pos = [1, 1]
        self.enemy_pos = [GRID_HEIGHT-2, 1]
        self.exit_pos = (GRID_HEIGHT-2, GRID_WIDTH-2)
        
        self.state = "RUNNING" # FSM: RUNNING, WIN, LOSE
        self.enemy_path = []
        self.move_counter = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dr, dc = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dr = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]: dr = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]: dc = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: dc = 1
        
        if dr != 0 or dc != 0:
            new_pos = (self.player_pos[0] + dr, self.player_pos[1] + dc)
            if self.maze.is_walkable(*new_pos):
                self.player_pos = list(new_pos)
                if tuple(self.player_pos) == self.exit_pos:
                    self.state = "WIN"

    def update(self):
        if self.state != "RUNNING": return

        # AI recalculates path every frame for 'Aggressive AI' behavior
        self.enemy_path = PathFinder.a_star(self.maze, tuple(self.enemy_pos), tuple(self.player_pos))
        
        # Enemy movement speed control (moves every 4 ticks)
        self.move_counter += 1
        if self.move_counter >= 4:
            if len(self.enemy_path) > 1:
                self.enemy_pos = list(self.enemy_path[1])
            self.move_counter = 0

        if tuple(self.enemy_pos) == tuple(self.player_pos):
            self.state = "LOSE"

    def draw(self):
        self.screen.fill(CLR_WALL)
        
        # Render Maze
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.maze.grid[r][c] == 0:
                    pygame.draw.rect(self.screen, CLR_PATH, (c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        # Render Exit
        pygame.draw.rect(self.screen, CLR_EXIT, (self.exit_pos[1]*TILE_SIZE, self.exit_pos[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Render AI Visualization (Shortest Path line)
        if len(self.enemy_path) > 1:
            points = [(c*TILE_SIZE + TILE_SIZE//2, r*TILE_SIZE + TILE_SIZE//2) for r, c in self.enemy_path]
            pygame.draw.lines(self.screen, CLR_AI_PATH, False, points, 2)

        # Render Entities
        pygame.draw.circle(self.screen, CLR_PLAYER, (self.player_pos[1]*TILE_SIZE + TILE_SIZE//2, self.player_pos[0]*TILE_SIZE + TILE_SIZE//2), TILE_SIZE//3)
        pygame.draw.circle(self.screen, CLR_ENEMY, (self.enemy_pos[1]*TILE_SIZE + TILE_SIZE//2, self.enemy_pos[0]*TILE_SIZE + TILE_SIZE//2), TILE_SIZE//3)

        # Overlay for Win/Loss
        if self.state != "RUNNING":
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            self.screen.blit(s, (0,0))
            msg = "MISSION ACCOMPLISHED" if self.state == "WIN" else "TERMINATED BY AI"
            color = CLR_EXIT if self.state == "WIN" else CLR_ENEMY
            txt = self.font.render(msg, True, color)
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
