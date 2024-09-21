from pydantic import BaseModel, Field
from typing import List


class ExecutionGraphStep(BaseModel):
    stepname: str = Field(
        description="Name of step identify, must be unique in the graph"
    )
    image: str = Field(description="Docker image to run on step")
    replicas: int = Field(
        description="Number of container replicas to run on step", min=1, default=1
    )
    dependencies: List[str] = Field(
        description="Steps dependent on, will fail if a dependency fails", default=[]
    )
    env: dict[str, str] = Field(
        description="Environment variable to be accessible to executions\
            in this step",
        default={},
    )
    args: List[str] = Field(description="Arguments for running", default=[])
    command: List[str] = Field(description="Commands to run on startup", default=[])


class ExecutionGraph(BaseModel):
    graphname: str = Field(description="Name of graph, must be unique")
    steps: List[ExecutionGraphStep] = Field(description="Steps to execute", min_length=1)


class RunGraphParameters(BaseModel):
    pass


class RunGraphDetails(BaseModel):
    execution_id: str


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
    steps_status: List[StepStatus]
