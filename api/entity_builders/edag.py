from typing import Any

from kr8s.asyncio.objects import APIObject, new_class

from entity_builders.base import BaseEntityBuilder
from models.edag import (
    EDAG_API_VERSION,
    EDAG_KIND,
    EDAGRequest,
    EDAGResource,
    EDAGStepResource,
)


class EDAGBuilder(BaseEntityBuilder):
    def build_resource(self, request: EDAGRequest) -> EDAGResource:
        return EDAGResource(
            graphname=request.graphname,
            steps=[
                EDAGStepResource(
                    stepname=steprequest.stepname,
                    image=steprequest.image,
                    replicas=steprequest.replicas,
                    dependencies=steprequest.dependencies,
                    env=steprequest.env,
                    args=steprequest.args,
                    command=steprequest.command,
                )
                for steprequest in request.steps
            ],
        )

    def build_manifest(self, resource: EDAGResource, namespace: str) -> APIObject:
        EDAG = self.get_crd()
        manifest = EDAG(
            resource={
                "metadata": {"name": resource.graphname, "namespace": namespace},
                "spec": {
                    "steps": {
                        step.stepname: self._build_step_manifest(step)
                        for step in resource.steps
                    }
                },
            }
        )
        return manifest

    def _build_step_manifest(self, step: EDAGStepResource) -> dict[str, Any]:
        return {
            "argument": step.args,
            "command": step.command,
            "dependencies": step.dependencies,
            "envs": step.env,
            "image": step.image,
            "replicas": step.replicas,
        }

    @staticmethod
    def get_crd() -> type[APIObject]:
        return new_class(kind=EDAG_KIND, version=EDAG_API_VERSION)
