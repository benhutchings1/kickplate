from pydantic import BaseModel
from typing import List
from src.utils import read_schema


class CreateExecGraphInput(BaseModel):
    model_config = {"json_schema_extra":read_schema()}

class CreateExecGraphOutput(BaseModel):
    graph_definition: str


class RunExecGraphOutput(BaseModel):
    exec_id: str


class ExecGraphStatusInput(BaseModel):
    exec_id: str

class ExecGraphOverall(BaseModel):
    completed: bool
    phase: str
    creation_time: str
    
class StepDesc(BaseModel):
    name: str
    state: str
    start_time: str
    finish_time: str
    error_message: str

class ExecGraphStatusOutput(BaseModel):
    overall: ExecGraphOverall
    steps_status: List[StepDesc]
    

class ErrorStatusOutput(BaseModel):
    error: str
    