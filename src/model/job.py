from __future__ import annotations

from typing import TYPE_CHECKING

from ._base_agent import BaseAgent
from .enums import AgentEnum, JobStatesEnum, SubjectEnum

if TYPE_CHECKING:
    from .typings import JobParams, Message


class Job(BaseAgent):
    __slots__ = ("status", "job_params")

    status: JobStatesEnum
    job_params: JobParams

    def __init__(
        self,
        job_params: JobParams,
        debug: bool = False,
    ):
        self.job_params = job_params
        self.status = JobStatesEnum.AVAILABLE
        super().__init__(id=job_params["id"], type=AgentEnum.JOB, debug=debug)

    def next(self) -> None:
        pass

    def receive(self, msg: Message) -> None:
        super().receive(msg)
        # Check the job has been 'submitted'
        if self.job_params["submitted_at"] > self._clock.now:
            return
        match msg["subject"]:
            case SubjectEnum.MACHINE_IS_LOOKING_FOR_JOBS:
                self._machine_is_looking_for_jobs(msg=msg)
            case SubjectEnum.MACHINE_HAS_CHOSEN_A_JOB:
                self._machine_has_chosen_job(msg=msg)
            case SubjectEnum.JOB_COMPLETE:
                self.status = JobStatesEnum.COMPLETE
                if msg["body"]:
                    self.job_params["completed_at"] = int(
                        msg["body"]["completed_at"]
                    )
                if self._broker:
                    self.disconnect()
            case _:
                print("Method to handle message not implemented")
                exit()

    def _machine_is_looking_for_jobs(self, msg: Message) -> None:
        match self.status:
            case JobStatesEnum.AVAILABLE:
                response: Message = {
                    "thread": msg["thread"],
                    "to_agent": msg["from_agent"],
                    "from_agent": self.id,
                    "to_agent_type": AgentEnum.MACHINE,
                    "subject": SubjectEnum.JOB_IS_AVAILABLE,
                    "body": self.job_params,
                }
                if self._broker:
                    self.send(send_on=self._clock.now, msg=response)
            case _:
                pass

    def _machine_has_chosen_job(self, msg: Message) -> None:
        match self.status:
            case JobStatesEnum.AVAILABLE:
                if self._debug:
                    print(
                        "#"
                        + str(self._clock.now)
                        + ": "
                        + self.type
                        + " "
                        + str(self.id)
                        + ": Has accepted machine "
                        + str(msg["from_agent"])
                    )
                response: Message = {
                    "thread": msg["thread"],
                    "to_agent": msg["from_agent"],
                    "from_agent": self.id,
                    "to_agent_type": AgentEnum.MACHINE,
                    "subject": SubjectEnum.JOB_HAS_ACCEPTED_MACHINES_OFFER,
                    "body": self.job_params,
                }
                self.send(send_on=self._clock.now, msg=response)
                self.status = JobStatesEnum.SELECTED
                self.job_params["manufactured_by"] = msg["from_agent"]
                self.job_params["selected_at"] = self._clock.now
            case JobStatesEnum.SELECTED:
                response: Message = {
                    "thread": msg["thread"],
                    "to_agent": msg["from_agent"],
                    "from_agent": self.id,
                    "to_agent_type": AgentEnum.MACHINE,
                    "subject": SubjectEnum.JOB_HAS_DECLINED_MACHINES_OFFER,
                    "body": {},
                }
                self.send(send_on=self._clock.now, msg=response)
            case _:
                pass
