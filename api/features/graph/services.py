from typing import Annotated, Any, cast

from fastapi import Depends
from kr8s import ServerError
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from entity_builders.edag import EDAGBuilder
from entity_builders.edagrun import EDAGRunBuilder
from external.kubernetes import KubernetesClient
from features.graph.exceptions import (
    EDAGAlreadyExistsError,
    EDAGNotFoundError,
    UndeterminedApiError,
)
from models.edag import EDAGRequest, EDAGResource
from models.edagrun import EDAGRunResource, EDAGRunResponse
from models.status import GraphStatusDetails


class EDAGServices:
    def __init__(
        self,
        kubernetes_client: Annotated[KubernetesClient, Depends()],
        edag_builder: Annotated[EDAGBuilder, Depends()],
        edag_run_builder: Annotated[EDAGRunBuilder, Depends()],
    ) -> None:
        self._kubernetes_client = kubernetes_client
        self._edag_builder = edag_builder
        self._edag_run_builder = edag_run_builder

    async def create_edag(self, edag_request: EDAGRequest) -> None:
        edag_resource = self._edag_builder.build_resource(edag_request)
        await self._create_edag_resource(edag_resource)

    async def _create_edag_resource(self, edag_resource: EDAGResource) -> None:
        try:
            await self._kubernetes_client.create_resource(
                self._edag_builder, edag_resource
            )
        except ServerError as exc:
            status_code = self._try_get_status_code(exc)
            if status_code == HTTP_409_CONFLICT:
                raise EDAGAlreadyExistsError(edag_resource.graphname)
            raise UndeterminedApiError() from exc

    async def run_edag(self, edag_name: str) -> EDAGRunResponse:
        edag_uid = await self._get_edag_uid(edag_name)
        edag_run_resource = EDAGRunResource(edagname=edag_name, edag_uid=edag_uid)
        manifest = await self._create_edag_run(edag_run_resource)

        if manifest is None:
            # Name collision
            return await self.run_edag(edag_name)

        return EDAGRunResponse(id=manifest["metadata"]["name"])

    async def _get_edag_uid(self, edag_name: str) -> str:
        try:
            edag_details = await self._kubernetes_client.get_resource(
                self._edag_builder, edag_name
            )
        except ServerError as exc:
            status_code = self._try_get_status_code(exc)
            if status_code == HTTP_404_NOT_FOUND:
                raise EDAGNotFoundError(edag_name)
            raise UndeterminedApiError() from exc

        uid = edag_details.raw["metadata"]["uid"]
        return cast(str, uid)

    async def _create_edag_run(
        self, edag_run_resource: EDAGRunResource
    ) -> dict[str, Any] | None:
        try:
            edag_run_manifest = await self._kubernetes_client.create_resource(
                self._edag_run_builder, edag_run_resource
            )
            return edag_run_manifest
        except ServerError as exc:
            status_code = self._try_get_status_code(exc)
            if status_code == HTTP_409_CONFLICT:
                # Unlikely event of generatated name collision
                # Return none and trigger another attempt
                return None
            raise UndeterminedApiError() from exc

    def _try_get_status_code(self, exc: ServerError) -> int:
        if exc.response is not None:
            return exc.response.status_code
        if exc.status is not None:
            return int(cast(dict[str, str], exc.status)["code"])

        raise UndeterminedApiError() from exc
