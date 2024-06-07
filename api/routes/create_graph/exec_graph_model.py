from pydantic import BaseModel, Field
from typing import List


class ExecGraphStep(BaseModel):
    stepname: str = Field(
        description="Name of step identify, must be unique in the graph"
    )
    image: str = Field(description="Docker image to run on step")
    replicas: int = Field(
        description="Number of container replicas to run on step", min=1
    )
    dependencies: List[str] = Field(
        description="Steps dependent on, will fail if a dependency fails"
    )
    env: dict[str, str] = Field(
        description="Environment variable to be accessible to executions\
            in this step"
    )
    args: List[str] = Field(description="Arguments for running")
    command: List[str] = Field(description="Commands to run on startup")


class ExecGraph(BaseModel):
    graphname: str = Field(description="Name of graph, must be unique")
    steps: List[ExecGraphStep] = Field(description="Steps to execute", min_length=1)
