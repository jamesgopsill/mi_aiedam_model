from __future__ import annotations

from typing import TYPE_CHECKING

from .broker import broker
from .clock import clock
from .enums import AgentEnum

if TYPE_CHECKING:
    from .broker import Broker
    from .clock import Clock
    from .typings import Message


class BaseAgent:
    __slots__ = (
        "_broker",
        "_clock",
        "_debug",
        "id",
        "type",
        "messages_sent",
        "messages_received",
    )

    _broker: Broker
    _clock: Clock
    _debug: bool
    id: int
    type: AgentEnum
    messages_sent: int
    messages_received: int

    def __init__(
        self,
        id: int,
        type: AgentEnum,
        debug: bool = False,
    ) -> None:
        self._broker = broker
        self._clock = clock
        self._debug = debug
        self.id = id
        self.type = type
        self.messages_sent = 0
        self.messages_received = 0

    # Simulating the connection handshake
    def connect(self) -> None:
        self._broker.connect(agent=self)
        self.messages_sent += 1
        self.messages_received += 1

    def disconnect(self) -> None:
        self._broker.disconnect(agent=self)
        self.messages_sent += 1

    def send(self, send_on: int, msg: Message) -> None:
        if self._debug:
            print(
                f"#{self._clock.now}: {self.type} {self.id}: Sent -> {msg['subject']}"
            )
        self._broker.receive(send_on=send_on, msg=msg)

    def receive(self, msg: Message) -> None:
        self.messages_received += 1
        if self._debug:
            print(
                f"#{self._clock.now}: {self.type} {self.id}: Received -> {msg['subject']}"
            )
