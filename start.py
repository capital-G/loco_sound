import logging
import time
from datetime import datetime, timedelta

import pygame

from loco_sound.loco import LocoCollector, Loco
from loco_sound.z21 import Client, LocoInfo

log = logging.getLogger('loco_sound')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

if __name__ == '__main__':
    # see https://stackoverflow.com/a/49346100
    pygame.mixer.pre_init(44100, -16, 2, 256)
    pygame.mixer.init()

    client = Client()
    client.send_welcome()
    client.subscribe_to_all_locos()

    loco_collector = LocoCollector()
    loco_collector.add_locos(
        Loco(232),
        Loco(2),
    )

    welcome_time = datetime.now()
    try:
        while True:
            message = client.listen()
            if message:
                loco_info = LocoInfo.from_z21_response(message)
                loco_collector.update_locos(loco_info)

            loco_collector.execute_due_functions()

            if datetime.now() - welcome_time > timedelta(seconds=30):
                client.send_welcome()
                welcome_time = datetime.now()

            time.sleep(0.001)

    except KeyboardInterrupt:
        log.info('Starting shutdown')
