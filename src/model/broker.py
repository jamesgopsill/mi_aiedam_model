from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from .clock import clock
from .enums import AgentEnum

if TYPE_CHECKING:
    from ._base_agent import BaseAgent
    from .clock import Clock
    from .typings import Message


class Broker:
    __slots__ = (
        "_address_book",
        "_debug",
        "_message_buffer",
        "_clock",
        "messages_received",
        "messages_sent",
    )
    messages_received: int
    messages_sent: int
    _address_book: Dict[AgentEnum, Dict[int, BaseAgent]]
    _debug: bool
    _message_buffer: Dict[int, List[Message]]
    _clock: Clock

    def __init__(self, debug: bool = False) -> None:
        self._address_book = {
            AgentEnum.JOB: {},
            AgentEnum.MACHINE: {},
        }
        self._message_buffer = {}
        self.messages_received = 0
        self.messages_sent = 0
        self._debug = debug
        self._clock = clock

    def connect(self, agent: BaseAgent) -> None:
        if self._debug:
            print(
                f"#{self._clock.now} Broker: {agent.type} {agent.id}: Connected"
            )

        self._address_book[agent.type][agent.id] = agent
        self.messages_received += 1
        self.messages_sent += 1

    def disconnect(self, agent: BaseAgent) -> None:
        if self._debug:
            print(
                f"#{self._clock.now} Broker: {agent.type} {agent.id}: Disconnected"
            )
        self.messages_received += 1
        del self._address_book[agent.type][agent.id]

    def receive(self, send_on: int, msg: Message) -> None:
        self.messages_received += 1
        if send_on in self._message_buffer:
            self._message_buffer[send_on].append(msg)
        else:
            self._message_buffer[send_on] = [msg]

    def send(self, msg: Message) -> None:
        self.messages_sent += 1
        match msg["to_agent"]:
            case -1:
                for agent in self._address_book[msg["to_agent_type"]].values():
                    agent.receive(msg)
                    self.messages_sent += 1
            case _:
                if msg["to_agent"] in self._address_book[msg["to_agent_type"]]:
                    agent = self._address_book[msg["to_agent_type"]][
                        msg["to_agent"]
                    ]
                    agent.receive(msg)
                    self.messages_sent += 1

    def next(self) -> None:
        if self._clock.now in self._message_buffer:
            # Drain the message buffer for the specific time.
            # N.b. messages may be added as agents real-time respond to messages
            # Hence why we need to while loop iterate and drain the buffer.
            while len(self._message_buffer[self._clock.now]) > 0:
                msg = self._message_buffer[self._clock.now].pop(0)
                self.send(msg=msg)


broker = Broker()
