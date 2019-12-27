import logging
import socket
from typing import Optional

from loco_sound.z21.message import Message

log = logging.getLogger(__name__)


class Client:
    """
    Handles the communication to the Z21 in both ways via
    :func:`~send_message` and :func:`~listen`.

    :param host: Hostname of the z21 in your network.
    :param port: Port number of the z21
    """
    def __init__(self, host: str = '192.168.0.111', port: int = 21105):
        self.socket = socket.socket(
            socket.AF_INET,  # ipv4
            socket.SOCK_DGRAM,  # UDP
        )
        self.host = host
        self.port = port
        self.socket.bind(('', self.port))  # @todo why '' ?
        self.socket.setblocking(False)
        log.info(f'Initiated z21 client to {self.host}:{self.port}')

    def __del__(self):
        """
        Logs off z21 from client - because we are nice.
        """
        log.info('Log off Z21')
        self.send_message(Message(
            header=bytearray([0x30, 0x00])
        ))

    def listen(self) -> Optional[Message]:
        """
        Collects UDP messages which were send to us.

        .. todo::

            Maybe marry this properly into the main loop by providing
            callback

        :returns: If a message is available we will return this as a parsed
            :class:`~Message`.
            If no message is available we will return None.
        """
        # @todo make this generator or async?
        try:
            data, addr = self.socket.recvfrom(1024)  # buffer 1024 bytes
        except socket.error:
            return None
        else:
            message = Message.from_z21_message(bytearray(data))
            log.debug(f'Received {message}')
            return message

    def send_message(self, message: Message) -> None:
        """
        Sends a :class:`~Message` to the connected z21.

        :param message: Message which you want to send.
        """
        log.debug(f'Send to z21: {message}')
        self.socket.sendto(
            message.data,
            (self.host, self.port),
        )

    def send_welcome(self) -> None:
        """
        Sends welcome message to z21 so we are a registered client.
        We do this by asking for the serial number of the z21.

        We will call this periodically so we still receive messages
        from z21 after some time because otherwise we will get logged out
        as a client.
        """
        log.debug(f'Send z21 welcome message to {self.host}')
        self.send_message(
            Message(
                header=bytearray([0x10, 0x01])
            )
        )

    def subscribe_to_all_locos(self) -> None:
        """
        Sends message so we are subscribed to changes of all locomotives.
        You need to collect the messages from z21 via :func:`~listen`.
        """
        log.info(f'Subscribe to all locos')
        self.send_message(
            Message(
                header=bytearray([0x50, 0x00]),
                x_header=0x00,
                db_data=bytearray([0x01, 0x00, 0x01])
            )
        )

    def subscribe_to_loco(self, loco) -> None:
        """
        Subscribes to a single loco for changes.
        You need to collect the messages from z21 via :func:`~listen`.

        .. warning::

            Using this is not recommended because we will receive stacked
            messages  which are not yet supported.
            This also this limits our application to 15 locos.
            Use :func:`~subscribe_to_all_locos` instead.

        :param loco: Loco on which you want to receive changes from.
        """
        log.info(f'Subscribe to {loco}')
        self.send_message(
            Message(
                header=bytearray([0x40, 0x00]),
                x_header=0xe3,
                db_data=bytearray([
                    0xf0,
                    (loco.loco_number >> 8),  # adr msb
                    (loco.loco_number & 0b11111111),  # adr lsb
                ])
            )
        )
