import random
from string import ascii_lowercase, digits

from kr8s.asyncio.objects import APIObject, new_class

from entity_builders.base import BaseEntityBuilder
from models.base import BaseRequest
from models.edag import EDAG_API_VERSION, EDAG_KIND
from models.edagrun import EDAG_RUN_API_VERSION, EDAG_RUN_KIND, EDAGRunResource

_GENERATED_SUFFIX_LENGTH = 8


class EDAGRunBuilder(BaseEntityBuilder):
    def build_resource(self, request: BaseRequest) -> EDAGRunResource:
        """Ignore as there is no request body"""

        raise NotImplementedError

    def build_manifest(self, resource: EDAGRunResource, namespace: str) -> APIObject:
        EDAGRun = self.get_crd()
        manifest = EDAGRun(
            resource={
                "metadata": {
                    "name": self._generate_edagrun_name(resource.edagname),
                    "namespace": namespace,
                    "ownerReferences": [
                        {
                            "apiVersion": EDAG_API_VERSION,
                            "kind": EDAG_KIND,
                            "name": resource.edagname,
                            "uid": resource.edag_uid,
                        }
                    ],
                },
                "spec": {"edagname": resource.edagname},
            }
        )
        return manifest

    def _generate_edagrun_name(self, edagname: str) -> str:
        suffix = "".join(
            random.choices(
                population=ascii_lowercase + digits, k=_GENERATED_SUFFIX_LENGTH
            )
        )
        return f"{edagname}-{suffix}"

    @staticmethod
    def get_crd() -> type[APIObject]:
        return new_class(kind=EDAG_RUN_KIND, version=EDAG_RUN_API_VERSION)
