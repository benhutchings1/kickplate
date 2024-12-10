from pydantic import BaseModel


class EDAGStepEntity(BaseModel):
    stepname: str
    image: str
    replicas: int
    dependencies: list[str]
    env: dict[str, str]
    args: list[str]
    command: list[str]


class EDAGEntity(BaseModel):
    graphname: str
    steps: list[EDAGStepEntity]


class EDAGRunEntity(BaseModel):
    pass
