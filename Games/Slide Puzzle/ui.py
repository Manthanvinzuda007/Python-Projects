# ui.py
import pygame
from settings import *

def draw_glass_rect(surface, rect, radius=15):
    glass = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glass, GLASS_BG, glass.get_rect(), border_radius=radius)
    pygame.draw.rect(glass, GLASS_BORDER, glass.get_rect(), width=2, border_radius=radius)
    surface.blit(glass, rect.topleft)

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        color = (255, 255, 255, 50) if self.is_hovered else GLASS_BG
        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, color, btn_surf.get_rect(), border_radius=10)
        pygame.draw.rect(btn_surf, GLASS_BORDER, btn_surf.get_rect(), width=2, border_radius=10)
        surface.blit(btn_surf, self.rect.topleft)
        
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
