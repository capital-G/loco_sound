from typing import Dict
import logging

from loco_sound.z21.message import Message

log = logging.getLogger(__name__)


class LocoInfo:
    """
    Serializes locomotive status updates from a received
    :class:`loco_sound.z21.Message`, see :func:`~from_z21_response`.

    :param loco_address: Address which caused the information
    :param dcc_speed_steps: Speed steps of the loco
    :param direction: Driving direction of the loco.
        0 for backwards, 1 for forwards.
    :param speed: speed step which was send - will be absolute so please
        compare with ``dcc_speed_steps`` for relative speed.
    :param functions: Stores a dict of which informations are selected and which
        are currently not selected.
    """
    def __init__(
            self,
            loco_address: int,
            dcc_speed_steps: int,
            direction: int,
            speed: int,
            functions: Dict[int, bool],
    ):
        self.loco_address: int = loco_address
        self.dcc_speed_steps: int = dcc_speed_steps
        self.direction: int = direction  # 1 = forward
        self.speed: int = speed
        self.functions: Dict[int, bool] = functions

    @classmethod
    def from_z21_response(cls, message: Message):
        """
        Serializes a :class:`loco_sound.z21.Message`

        :param message: Message which you want to serialize.
        """
        try:
            assert message.header == bytearray([0x40, 0x00])
            assert message.x_header == 0xef
        except AssertionError:
            # @todo gets called when stop is hit
            raise AssertionError(f'Invalid z21 message for loco info: {message}')

        dcc_data = message.db_data[2] & 0b00000111
        speed_data = message.db_data[3] & 0b01111111

        speed = 0
        if dcc_data == 1:
            dcc_speed_steps = 14
            speed = max(0, speed_data-1)
        elif dcc_data == 2:
            dcc_speed_steps = 28
            # @todo this needs to be done properly
            speed = max(0, 2*((0b00001111 & speed_data) - 1))
        elif dcc_data == 4:
            dcc_speed_steps = 126
            speed = max(0, speed_data - 1)
        else:
            log.critical(f'Unknown DCC Step value: {dcc_data} - byte is {message.db_data[2]}')
            dcc_speed_steps = 128

        functions = {}
        if len(message.db_data) >= 5:
            # check if bits are set
            functions[0] = bool(message.db_data[4] & 0b00010000)
            functions[4] = bool(message.db_data[4] & 0b00001000)
            functions[3] = bool(message.db_data[4] & 0b00000100)
            functions[2] = bool(message.db_data[4] & 0b00000010)
            functions[1] = bool(message.db_data[4] & 0b00000001)

        for db_num, db_bit in enumerate(message.db_data[5:]):
            for bit_num in range(8):
                functions[5 + (8 * db_num) + bit_num] = bool(db_bit & (2 ** bit_num))

        return cls(
            loco_address=(message.db_data[0] & 0x3f << 8) + message.db_data[1],
            dcc_speed_steps=dcc_speed_steps,
            direction=message.db_data[3] >> 7 & 1,
            speed=speed,
            functions=functions,
        )

    def __str__(self):
        return 'LocoInfo for loco #{address}: speed {speed}/{steps}, direction: {direction}, active functions: {functions}'.format(
            address=self.loco_address,
            speed=self.speed,
            steps=self.dcc_speed_steps,
            direction=self.direction,
            functions=(sorted([k for k, v in self.functions.items() if v])),
        )
