from entity_builders.base import BaseRequest, BaseResource
from models.base import BaseResponse

EDAG_RUN_KIND = "EDAGRun"
EDAG_RUN_API_VERSION = "edag.kickplate.com/v1alpha1"


class EDAGRunResource(BaseResource):
    edagname: str
    edag_uid: str


class EDAGRunResponse(BaseResponse):
    id: str
