import collections
import logging
from collections import defaultdict
from copy import copy
from typing import Callable, List, Dict, Optional, Deque, Tuple
from datetime import datetime, timedelta
import itertools

import pygame

from loco_sound.z21 import LocoInfo

log = logging.getLogger(__name__)


class Loco:
    """
    This class has all the loco logic

    :param loco_number: The number of the locomotive you want to control.
    :param scheduled_function_calls: Scheduled function calls.
    """
    def __init__(self, loco_number: int):

        self.loco_type_name: str = ''
        self._loco_number: int = loco_number
        self._functions: dict = defaultdict(lambda: False)
        self._speed: int = 0
        self._speed_stack: Deque[Tuple[datetime, int]] = collections.deque(maxlen=5)
        self.direction = 1  # 1 for forward, 0 for backward
        self._last_steam_sound_time: Optional[datetime] = None
        self._functions_observer: Dict[int, List[Callable]] = defaultdict(list)
        self.scheduled_function_calls: Dict[datetime, Callable] = {}
        self.f_sounds: Dict[int, pygame.mixer.Sound] = {
            7: pygame.mixer.Sound('horn.wav'),
            9: pygame.mixer.Sound('idle.wav'),
            6: pygame.mixer.Sound('train.wav')
        }
        self.steam_sounds = [
            pygame.mixer.Sound('cyl_1_n.wav'),
            pygame.mixer.Sound('cyl_2.wav'),
            # pygame.mixer.Sound('cyl_2_n.wav')
        ]
        self.steam_iterator = iter(itertools.cycle(self.steam_sounds))
        self.break_sound = pygame.mixer.Sound('brakes.wav')
        self.break_sound.set_volume(0.2)
        self.start_sound = pygame.mixer.Sound('steam.wav')
        self.start_sound.set_volume(0.15)
        self._old_delta: Optional[timedelta] = None

    def update_from_loco_info(self, loco_info: LocoInfo):
        self.functions = loco_info.functions
        self.speed = loco_info.speed
        assert loco_info.direction in (1, 0)
        self.direction = loco_info.direction

    def bind_to_functions(self, callback, function_num: int):
        log.debug(f'Bound {callback} to functions change of loco {self.loco_number} and function {function_num}')
        self._functions_observer[function_num].append(callback)

    @property
    def loco_number(self):
        # makes loco number "immutable"
        return self._loco_number

    @property
    def functions(self):
        return self._functions

    @functions.setter
    def functions(self, value: dict):
        diff_keys = [k for k in value.keys() if self._functions.get(k) != value[k]]
        for diff_key in diff_keys:
            if diff_key < 10:
                getattr(Loco, f'change_f_{diff_key}')(
                    self=self,
                    new_value=value[diff_key],
                    old_value=self._functions.get(diff_key, False),
                    all_functions=value
                )
            for callback in self._functions_observer.get(diff_key, []):
                callback(
                    new_value=value[diff_key],
                    old_value=self._functions.get(diff_key, False),
                    all_functions=value,
                )
        self._functions = value

    @property
    def speed(self):
        return self.speed

    @speed.setter
    def speed(self, value: int):
        old_value = copy(self._speed)  # @todo is copy mandatory?
        self._speed = value
        if value != old_value:
            self.speed_changed(value, old_value)

    def change_f_0(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        """
        Foo

        :param new_value: Foo
        """
        pass

    def change_f_1(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        pass

    def change_f_2(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        pass

    def change_f_3(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        pass

    def change_f_4(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        pass

    def change_f_5(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        pass

    def change_f_6(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        if 6 in self.f_sounds:
            if new_value is True:
                log.info(f'Start train ambient for {self}')
                self.f_sounds[6].play(loops=-1)
            else:
                log.info(f'Stop train ambient for {self}')
                self.f_sounds[6].stop()

    def change_f_7(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        if 7 in self.f_sounds:
            log.info(f'Play horn of {self}')
            self.f_sounds[7].play()

    def change_f_8(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        pass

    def change_f_9(self, new_value: bool, old_value: bool, all_functions: Dict[int, bool], *args, **kwargs):
        if 9 in self.f_sounds:
            if new_value is True:
                log.info(f'Start ambient for {self}')
                self.f_sounds[9].play(loops=-1)
            else:
                log.info(f'Stop ambient for {self}')
                self.f_sounds[9].stop()

    def speed_changed(self, new_value: int, old_value: int):
        log.debug(f'Speed @ {new_value} for {self}')
        self._speed_stack.append((datetime.now(), new_value))
        self._play_and_schedule_next_sound(speed_update=True, old_speed=old_value)

    def _play_and_schedule_next_sound(self, speed_update: bool = False, old_speed: Optional[int] = None):
        if self._speed <= 0:
            # when stopping play brake sound and stop scheduling steam sounds
            # self.break_sound.play()
            self._old_delta = None
            self._last_steam_sound_time = None
            return

        # now_delta = timedelta(
        #     milliseconds= int(1800 + (self._speed/126 * (-9500.5)))
        # )
        now_delta = timedelta(
            milliseconds=int((4.6 * self._speed**(-0.75))*1000)
        )
        print(now_delta)

        self.scheduled_function_calls = {}
        if speed_update:
            if self._last_steam_sound_time is None or self._old_delta is None:
                # if starting we want to play a steam sound immediately
                self.start_sound.play()
                self.steam_iterator.__next__().play()
                self._old_delta = now_delta
                self._last_steam_sound_time = datetime.now()
            next_sound_time = self._last_steam_sound_time + ((now_delta + self._old_delta) / 2)
        else:
            self.steam_iterator.__next__().play()
            self._last_steam_sound_time = datetime.now()
            next_sound_time = datetime.now() + now_delta
            self._old_delta = now_delta

        self.scheduled_function_calls[next_sound_time] = self._play_and_schedule_next_sound

    def __str__(self):
        return f'Loco #{self.loco_number}'

    def __repr__(self):
        return self.__str__()
