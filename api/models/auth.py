from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    KICKPLATE_USER = "kickplate:user"
    KICKPLATE_ADMIN = "kickplate:admin"


class TokenContents(BaseModel, extra="allow"):
    email: str
    roles: list[str]


class User(BaseModel):
    email: str
    roles: list[Role]
    token: str
