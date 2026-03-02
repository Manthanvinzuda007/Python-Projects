
# sound_manager.py
import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sound('slide', 'assets/sounds/slide.wav')
        self.load_sound('win', 'assets/sounds/win.wav')
        self.load_sound('click', 'assets/sounds/click.wav')

    def load_sound(self, name, path):
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)
        else:
            self.sounds[name] = None

    def play(self, name):
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()
