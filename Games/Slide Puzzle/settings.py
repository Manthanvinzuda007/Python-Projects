# settings.py
import pygame

# Window Settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
FPS = 60
TITLE = "Modern Slide Puzzle"

# Colors
BG_TOP = (15, 23, 42)
BG_BOTTOM = (30, 41, 59)
WHITE = (255, 255, 255)
GLASS_BG = (255, 255, 255, 25) # Transparent white for glassmorphism
GLASS_BORDER = (255, 255, 255, 80)
TILE_COLOR = (56, 189, 248)
TILE_HOVER = (14, 165, 233)
TEXT_COLOR = (241, 245, 249)

# Board Settings
BOARD_PADDING = 15
BOARD_SIZE = 450
BOARD_X = (WINDOW_WIDTH - BOARD_SIZE) // 2
BOARD_Y = (WINDOW_HEIGHT - BOARD_SIZE) // 2 + 30
