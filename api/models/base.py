from pydantic import BaseModel


class BaseRequest(BaseModel):
    """Base class for all request models"""

    pass


class BaseResource(BaseModel):
    """Base class for all resource models"""

    pass


class BaseResponse(BaseModel):
    """Base class for all response models"""

    pass
