from pydantic import BaseModel, Field


class EDAGRequestStep(BaseModel):
    stepname: str = Field(
        description="Name of step identify, must be unique in the graph"
    )
    image: str = Field(description="Docker image to run on step")
    replicas: int = Field(
        description="Number of container replicas to run on step",
        min_length=1,
        default=1,
    )
    dependencies: list[str] = Field(
        description="Steps dependent on, will fail if a dependency fails", default=[]
    )
    env: dict[str, str] = Field(
        description="Environment variable accessible by all replicas of this step\
            in this step",
        default={},
    )
    args: list[str] = Field(description="Arguments for running", default=[])
    command: list[str] = Field(description="Commands to run on startup", default=[])


class EDAGRequest(BaseModel):
    graphname: str = Field(description="Name of graph, must be unique")
    steps: list[EDAGRequestStep] = Field(description="Steps to execute", min_length=1)


class RunGraphParameters(BaseModel):
    pass


class RunGraphDetails(BaseModel):
    id: str


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
