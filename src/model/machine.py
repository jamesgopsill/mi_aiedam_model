from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, List
from uuid import uuid4

from ._base_agent import BaseAgent
from .enums import AgentEnum, MachineStateEnum, SubjectEnum

if TYPE_CHECKING:
    from .typings import Message


class Machine(BaseAgent):
    # if value assigned here then it is made available to all instances of Machine.
    status: MachineStateEnum
    print_time_remaining: int
    jobs_brokered: List[int]
    responses: List[Message]
    response_thread_id: str
    wait: int
    rejections: int
    _logic: Callable[[Machine], int]

    def __init__(
        self,
        id: int,
        logic: Callable[[Machine], int],
        debug: bool = False,
    ):
        self._logic = logic.__get__(
            self, Machine
        )  # binding self to the incoming function.
        self.status = MachineStateEnum.AVAILABLE
        self.print_time_remaining = -1
        self.jobs_brokered = []
        self.responses = []
        self.wait = -1
        self.rejections = 0
        super().__init__(id=id, type=AgentEnum.MACHINE, debug=debug)

    def next(self) -> None:
        match self.status:
            case MachineStateEnum.AVAILABLE:
                # If the time is between 9am and 5pm
                remainder = self._clock.now % (24 * 60)
                if remainder > 9*60 and remainder < 17*60:
                    self._machine_is_available()
            case MachineStateEnum.WAITING_FOR_RESPONSES:
                self._machine_is_waiting_for_responses()
            case MachineStateEnum.BUSY:
                self._busy()
            case MachineStateEnum.WAITING_FOR_ACCEPTANCE:
                pass
            case _:
                print("Should not get here.")
                exit()

    # On receiving a message from the broker.
    def receive(self, msg: Message) -> None:
        super().receive(msg)
        match msg["subject"]:
            case SubjectEnum.JOB_IS_AVAILABLE:
                self.responses.append(msg)
            case SubjectEnum.JOB_HAS_ACCEPTED_MACHINES_OFFER:
                self.status = MachineStateEnum.BUSY
                if "print_time" in msg["body"]:
                    self.print_time_remaining = int(msg["body"]["print_time"])
                else:
                    print("Job did not provide a print time")
                    exit()
                self.jobs_brokered.append(msg["from_agent"])
                self.responses = []
            case SubjectEnum.JOB_HAS_DECLINED_MACHINES_OFFER:
                self.rejections += 1
                self.status = MachineStateEnum.AVAILABLE
                self.responses = []
            case _:
                print("Should not get here.")
                exit()

    def _machine_is_available(self):
        self.responses = []
        self.wait = self._clock.now + 1
        self.response_thread_id = str(uuid4())
        self.status = MachineStateEnum.WAITING_FOR_RESPONSES
        msg: Message = {
            "thread": self.response_thread_id,
            "from_agent": self.id,
            "to_agent": -1,
            "to_agent_type": AgentEnum.JOB,
            "subject": SubjectEnum.MACHINE_IS_LOOKING_FOR_JOBS,
            "body": {},
        }
        self.send(send_on=self._clock.now, msg=msg)

    def _machine_is_waiting_for_responses(self):
        if self.wait != self._clock.now:
            self.wait -= 1
            return

        if self._debug:
            print(
                f"#{self._clock.now}: {self.type} {self.id}: {len(self.responses)} responses"
            )

        # Check if there are any messages that have appeared
        # and are not of interest
        invalid_responses: List[int] = []
        for idx, msg in enumerate(self.responses):
            if msg["thread"] != self.response_thread_id:
                invalid_responses.append(idx)
        invalid_responses = sorted(invalid_responses)
        for iv in invalid_responses:
            self.responses.pop(iv)

        if self.responses:
            job_id = self._logic()  # type: ignore
            # (Cannot define self on Callable as it thinks its a param to feed in.)
            if job_id != -1:
                self.status = MachineStateEnum.WAITING_FOR_ACCEPTANCE
                msg: Message = {
                    "thread": self.response_thread_id,
                    "from_agent": self.id,
                    "to_agent": job_id,
                    "to_agent_type": AgentEnum.JOB,
                    "subject": SubjectEnum.MACHINE_HAS_CHOSEN_A_JOB,
                    "body": {},
                }
                self.send(send_on=self._clock.now, msg=msg)
        else:
            self.status = MachineStateEnum.AVAILABLE
        self.responses = []
        self.wait = -1

    def _busy(self):
        self.print_time_remaining -= 1
        if self.print_time_remaining == 0:
            self.status = MachineStateEnum.AVAILABLE
            msg: Message = {
                "thread": self.response_thread_id,
                "from_agent": self.id,
                "to_agent": self.jobs_brokered[-1],
                "to_agent_type": AgentEnum.JOB,
                "subject": SubjectEnum.JOB_COMPLETE,
                "body": {"completed_at": self._clock.now},
            }
            self.print_time_remaining = -1
            self.send(send_on=self._clock.now, msg=msg)
