from pydantic import BaseModel


class StepStatus(BaseModel):
    name: str
    state: str
    start_time: str
    finish_time: str
    error_message: str


class GraphStatusDetails(BaseModel):
    graphname: str
    completed_time: str
    phase: str
    creation_time: str
    steps_status: list[StepStatus]
