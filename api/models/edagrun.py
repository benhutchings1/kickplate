from entity_builders.base import BaseResource, BaseRequest
from models.base import BaseResponse

EDAG_RUN_KIND = "EDAGRun"
EDAG_RUN_API_VERSION = "edag.kickplate.com/v1alpha1"


class EDAGRunResource(BaseResource):
    edagname: str


class EDAGRunResponse(BaseResponse):
    id: str


class EDAGRunRequest(BaseRequest):
    edagname: str
