from .models import EDAGEntity, EDAGStepEntity
from features.graph.models import EDAGRequest


def build_edag_resource(edag_request: EDAGRequest) -> EDAGEntity:
    return EDAGEntity(
        graphname=edag_request.graphname,
        steps=[
            EDAGStepEntity(
                stepname=steprequest.stepname,
                image=steprequest.image,
                replicas=steprequest.replicas,
                dependencies=steprequest.dependencies,
                env=steprequest.env,
                args=steprequest.args,
                command=steprequest.command,
            )
            for steprequest in edag_request.steps
        ],
    )


def build_edag_run_resource():
    pass
