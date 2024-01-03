from enum import Enum


class AgentEnum(str, Enum):
    JOB = "job"
    MACHINE = "machine"
    BROKER = "broker"


class JobStatesEnum(str, Enum):
    AVAILABLE = "available"
    SELECTED = "selected"
    COMPLETE = "complete"


class SubjectEnum(str, Enum):
    JOB_IS_AVAILABLE = "job_is_available"
    MACHINE_IS_LOOKING_FOR_JOBS = "machine_is_looking_for_jobs"
    MACHINE_HAS_CHOSEN_A_JOB = "machine_has_chosen_a_job"
    JOB_HAS_ACCEPTED_MACHINES_OFFER = "job_has_accepted_machines_offer"
    JOB_HAS_DECLINED_MACHINES_OFFER = "job_has_declined_machines_offer"
    JOB_COMPLETE = "job_complete"


class MachineStateEnum(str, Enum):
    AVAILABLE = "available"
    WAITING_FOR_RESPONSES = "waiting_for_responses"
    WAITING_FOR_ACCEPTANCE = "waiting_for_acceptance"
    BUSY = "busy"
