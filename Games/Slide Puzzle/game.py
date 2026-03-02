
import pygame
import time
import random 
from settings import *
from board import Board
from ui import Button, draw_glass_rect
from effects import EffectManager
from sound_manager import SoundManager

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Assets & Managers
        self.font_main = pygame.font.SysFont("Segoe UI", 40, bold=True)
        self.font_ui = pygame.font.SysFont("Segoe UI", 24)
        self.font_title = pygame.font.SysFont("Segoe UI", 60, bold=True)
        self.sound = SoundManager()
        self.effects = EffectManager()
        
        # Game State
        self.grid_size = 4
        self.board = Board(self.grid_size, self.font_main, self.sound)
        self.start_time = time.time()
        
        # UI
        self.btn_restart = Button(20, WINDOW_HEIGHT - 70, 120, 50, "Restart (R)", self.font_ui)
        self.btn_shuffle = Button(160, WINDOW_HEIGHT - 70, 120, 50, "Shuffle (S)", self.font_ui)
        self.btn_mode = Button(300, WINDOW_HEIGHT - 70, 150, 50, "Mode: 4x4", self.font_ui)

    def draw_bg(self):
        # Soft gradient background
        for y in range(WINDOW_HEIGHT):
            blend = y / WINDOW_HEIGHT
            r = int(BG_TOP[0] * (1 - blend) + BG_BOTTOM[0] * blend)
            g = int(BG_TOP[1] * (1 - blend) + BG_BOTTOM[1] * blend)
            b = int(BG_TOP[2] * (1 - blend) + BG_BOTTOM[2] * blend)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                self.btn_restart.check_hover(pos)
                self.btn_shuffle.check_hover(pos)
                self.btn_mode.check_hover(pos)
                # Tile hover
                for row in self.board.tiles:
                    for tile in row:
                        tile.is_hovered = pygame.Rect(tile.x, tile.y, tile.size, tile.size).collidepoint(pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if self.btn_restart.rect.collidepoint(pos):
                        self.restart()
                    elif self.btn_shuffle.rect.collidepoint(pos):
                        self.restart()
                    elif self.btn_mode.rect.collidepoint(pos):
                        self.change_mode()
                    else:
                        # Check tile click
                        for r in range(self.board.grid_size):
                            for c in range(self.board.grid_size):
                                tile = self.board.tiles[r][c]
                                if pygame.Rect(tile.x, tile.y, tile.size, tile.size).collidepoint(pos):
                                    self.board.move_tile(r, c)

            if event.type == pygame.KEYDOWN:
                er, ec = self.board.empty_pos
                if event.key == pygame.K_r: self.restart()
                if event.key == pygame.K_s: self.restart()
                if not self.board.is_solved:
                    if event.key == pygame.K_UP and er < self.board.grid_size - 1:
                        self.board.move_tile(er + 1, ec)
                    elif event.key == pygame.K_DOWN and er > 0:
                        self.board.move_tile(er - 1, ec)
                    elif event.key == pygame.K_LEFT and ec < self.board.grid_size - 1:
                        self.board.move_tile(er, ec + 1)
                    elif event.key == pygame.K_RIGHT and ec > 0:
                        self.board.move_tile(er, ec - 1)

    def restart(self):
        self.sound.play('click')
        self.board.generate_board()
        self.start_time = time.time()

    def change_mode(self):
        self.sound.play('click')
        self.grid_size += 1
        if self.grid_size > 5: self.grid_size = 3
        self.btn_mode.text = f"Mode: {self.grid_size}x{self.grid_size}"
        self.board = Board(self.grid_size, self.font_main, self.sound)
        self.start_time = time.time()

    def draw_hud(self):
        # Draw Glass Board backing
        draw_glass_rect(self.screen, pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE))
        
        # HUD Top
        title_surf = self.font_title.render("SLIDE PUZZLE", True, TEXT_COLOR)
        self.screen.blit(title_surf, (WINDOW_WIDTH//2 - title_surf.get_width()//2, 30))
        
        elapsed = int(time.time() - self.start_time) if not self.board.is_solved else "Done!"
        hud_text = f"Moves: {self.board.moves}   |   Time: {elapsed}s"
        hud_surf = self.font_ui.render(hud_text, True, TEXT_COLOR)
        self.screen.blit(hud_surf, (WINDOW_WIDTH//2 - hud_surf.get_width()//2, 100))

        # Buttons
        self.btn_restart.draw(self.screen)
        self.btn_shuffle.draw(self.screen)
        self.btn_mode.draw(self.screen)

    def update(self):
        self.board.update()
        if self.board.is_solved and random.random() < 0.05:
            # Trigger celebration continuously if won
            self.effects.spawn_confetti(WINDOW_WIDTH//2, BOARD_Y)

    def draw(self):
        self.draw_bg()
        self.effects.update_and_draw(self.screen)
        self.draw_hud()
        self.board.draw(self.screen)
        
        if self.board.is_solved:
            win_surf = self.font_title.render("PUZZLE SOLVED!", True, (134, 239, 172))
            rect = win_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            
            # Subtle shadow for text
            shadow = self.font_title.render("PUZZLE SOLVED!", True, (0,0,0))
            self.screen.blit(shadow, (rect.x + 3, rect.y + 3))
            self.screen.blit(win_surf, rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
