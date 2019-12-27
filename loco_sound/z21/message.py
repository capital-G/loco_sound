import struct
from typing import Optional
import logging

log = logging.getLogger(__name__)


class Message:
    """
    Serializes and builds messages for Z21.
    For serializing see :func:`~from_z21_message`.

    See `Z21 LAN reference sheet <https://www.z21.eu/media/Kwc_Basic_DownloadTag_Component/root-en-main_47-1652-959-downloadTag-download/default/d559b9cf/1558675126/z21-lan-protokoll-en.pdf>`_
    for more information.

    :param header: Header
    :param x_header: X_header
    :param db_data: db_data
    :param xor: xor byte
    :param length: 2 length bytes.
    """

    def __init__(
            self,
            header: bytearray,
            x_header: int = None,
            db_data: bytearray = None,
            xor: Optional[int] = None,
            length: Optional[bytearray] = None
    ):
        self.length: bytearray = length
        self.header: bytearray = header
        assert len(self.header) == 2
        self.x_header: Optional[int] = x_header
        self.db_data: bytearray = db_data if db_data else bytearray([])
        if self.db_data and self.x_header is None:
            print(db_data, x_header)
            raise AssertionError('Can not set db_data without x_header')
        self.xor: Optional[int] = xor

    @classmethod
    def from_z21_message(cls, message: bytearray):
        """
        Parses a received Z21 message.

        :param message: Raw byte UDP package received from Z21.
        """
        assert len(message) > 4
        x_header = None
        db_data = None
        xor = None
        if len(message) >= 5:
            x_header = message[4]
            xor = message[-1]
        if len(message) > 6:
            # x_header implies xor bit so we have at least 7 bytes now
            db_data = message[5:-1]

        return cls(
            length=message[0:2],
            header=message[2:4],
            x_header=x_header,
            db_data=db_data,
            xor=xor,
        )

    @property
    def data(self) -> bytearray:
        """
        Builds a byte representation of the message which can be send to Z21.

        :return: Message as raw bytes.
        """
        data = bytearray([])
        data.extend([
            *self.header,
        ])
        if self.x_header:
            data.append(self.x_header)
        data.extend(self.db_data)
        if self.x_header:
            # we need to add a xor if we send x-header data
            # if  xor is not given we need to calculate it
            data.append(self.xor if self.xor else self._calculate_xor())
        data[0:0] = self._calculate_length(data)
        return data

    def _calculate_xor(self) -> int:
        """
        Calculates XOR byte at the end of a message which acts as a checksum.
        """
        xor = self.x_header
        for db_d in self.db_data:
            xor ^= db_d
        return xor

    @staticmethod
    def _calculate_length(data: bytearray) -> bytearray:
        """
        Calculates length of a Z21 message.
        """
        return bytearray(struct.pack('<H', len(data) + 2))

    def __str__(self):
        return 'Z21 message - header: {header} - x_header: {x_header} - db_data: {db_data} - raw: {raw}'.format(
            header=' '.join('0x{:02x}'.format(x) for x in self.header),
            x_header=hex(self.x_header) if self.x_header is not None else 'not set',
            db_data=' '.join('0x{:02x}'.format(x) for x in self.db_data),
            raw=' '.join('0x{:02x}'.format(x) for x in bytearray(self.data)),
        )
