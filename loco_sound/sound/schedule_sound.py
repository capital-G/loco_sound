from datetime import datetime

import pygame


class ScheduleSound:
    def __init__(self, date_time: datetime, sound: pygame.mixer.Sound):
        self.date_time = date_time
        self.sound = sound
