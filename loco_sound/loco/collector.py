import logging
from datetime import datetime
from typing import Dict, List, Callable, Generator

from loco_sound.loco import Loco
from loco_sound.z21 import LocoInfo

log = logging.getLogger(__name__)


class LocoCollector:
    """
    This class maps a :class:`~Loco` to a :class:`SoundPackage`,
    passes updates in form of :class:`~loco_sound.z21.LocoInfo` to a within a LocoCollector registered
    :class:`~Loco` and also checks if some scheduled functions needs to be called.
    This is necessary on a :class:`~SteamLoco`.
    """
    def __init__(self):
        self._locos: Dict[int, Loco] = dict()

    def add_locos(self, *locos: Loco):
        """
        Registers a :class:`~loco_sound.loco.Loco` for information monitoring.
        """
        for loco in locos:
            self._locos[loco.loco_number] = loco

    def update_locos(self, *loco_infos: LocoInfo):
        """
        Passes the received :class:`~LocoInfo` update to a registered :class:`~Loco` in our collector.
        If the ``loco_address`` of :class:`~LocoInfo` is not registered we will ignore the info.

        :param loco_infos: Received updates
        """
        for loco_info in loco_infos:
            log.debug(f'Loco Update: {loco_info}')
            if loco_info.loco_address in self._locos:
                self._locos[loco_info.loco_address].update_from_loco_info(loco_info)

    def execute_due_functions(self):
        """
        Each registered :class:`~Loco` can store a set of functions
        in the attribute ``scheduled_function_calls`` which should be executed in the future
        at a given timestamp.

        We check if these functions are due and if so we will execute them.
        """
        functions: List[Callable] = []
        for loco in self._locos.values():
            loco_function_times: List[datetime] = []
            # if loco.scheduled_function_calls:
            #     print(loco.scheduled_function_calls)
            for function_time, function in loco.scheduled_function_calls.items():
                if function_time <= datetime.now():
                    # log.debug(f'{function} is now due')
                    functions.append(function)
                    loco_function_times.append(function_time)
            for f in loco_function_times:
                loco.scheduled_function_calls.pop(f)
        for f in functions:
            f()

    def __getitem__(self, item):
        if item not in self._locos.keys():
            log.debug(f'Add loco #{item} to loco collector')
            self._locos[item] = Loco(item)
        return self._locos[item]
