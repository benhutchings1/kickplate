from enum import Enum

from pydantic import BaseModel


class TokenContents(BaseModel, extra="allow"):
    email: str
    roles: list[str]
    scopes: list[str] = []


class Scopes(str, Enum):
    EDAG_READ = "kickplate:edag:read"
    EDAG_WRITE = "kickplate:edag:write"
    EDAG_DELETE = "kickplate:edag:delete"
    EDAG_RUN = "kickplate:edag:run"


class Roles(str, Enum):
    KICKPLATE_USER = "kickplate:user"
    KICKPLATE_ADMIN = "kickplate:admin"


class User(BaseModel):
    email: str
    scopes: list[Scopes]
    roles: list[Roles]
    token: str
