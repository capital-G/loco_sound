import pygame


class FunctionSound(pygame.mixer.Sound):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
