from typing import Dict, TypedDict

from .enums import AgentEnum, SubjectEnum


class JobParams(TypedDict):
    id: int
    print_time: int
    submitted_at: int
    selected_at: int
    manufactured_by: int
    completed_at: int


class Message(TypedDict):
    thread: str
    from_agent: int
    to_agent: int
    to_agent_type: AgentEnum
    subject: SubjectEnum
    body: Dict[str, str | int] | JobParams
