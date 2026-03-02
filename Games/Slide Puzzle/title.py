
# tile.py
import pygame
from settings import *

class Tile:
    def __init__(self, number, row, col, size, font):
        self.number = number
        self.row = row
        self.col = col
        self.size = size
        self.font = font
        
        # Actual screen position (starts at target)
        self.x = BOARD_X + BOARD_PADDING + col * size
        self.y = BOARD_Y + BOARD_PADDING + row * size
        
        self.target_x = self.x
        self.target_y = self.y
        self.is_hovered = False

    def update_target(self, row, col):
        self.row = row
        self.col = col
        self.target_x = BOARD_X + BOARD_PADDING + col * self.size
        self.target_y = BOARD_Y + BOARD_PADDING + row * self.size

    def update(self):
        # Smooth Easing (lerp)
        self.x += (self.target_x - self.x) * 0.2
        self.y += (self.target_y - self.y) * 0.2

    def draw(self, surface):
        if self.number == 0: return # Don't draw empty tile
        
        rect = pygame.Rect(self.x, self.y, self.size - 5, self.size - 5)
        color = TILE_HOVER if self.is_hovered else TILE_COLOR
        
        # Draw tile base
        pygame.draw.rect(surface, color, rect, border_radius=10)
        
        # Text
        text = self.font.render(str(self.number), True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
