# main.py
import pygame
import sys

# Ensure Pygame is initialized before importing the Game logic
pygame.init()

from game import Game

if __name__ == "__main__":
    app = Game()
    app.run()
    pygame.quit()
    sys.exit()
  
