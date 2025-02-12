from pydantic import Field

from entity_builders.base import BaseRequest, BaseResource

EDAG_KIND = "EDAG"
EDAG_API_VERSION = "edag.kickplate.com/v1alpha1"


class EDAGRequestStep(BaseRequest):
    stepname: str = Field(
        description="Name of step identify, must be unique in the graph"
    )
    image: str = Field(description="Docker image to run on step")
    replicas: int = Field(
        description="Number of container replicas to run on step",
        ge=1,
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


class EDAGRequest(BaseRequest):
    graphname: str = Field(description="Name of graph, must be unique")
    steps: list[EDAGRequestStep] = Field(description="Steps to execute", min_length=1)


class EDAGStepResource(BaseResource):
    stepname: str
    image: str
    replicas: int
    dependencies: list[str]
    env: dict[str, str]
    args: list[str]
    command: list[str]


class EDAGResource(BaseResource):
    graphname: str
    steps: list[EDAGStepResource]
