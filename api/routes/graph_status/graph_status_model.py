from pydantic import BaseModel
from typing import List


class StepStatus(BaseModel):
    name: str
    state: str
    start_time: str
    finish_time: str
    error_message: str


class GraphStatusModel(BaseModel):
    graphname: str
    completed_time: str
    phase: str
    creation_time: str
    steps_status: List[StepStatus]