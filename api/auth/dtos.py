from pydantic import BaseModel
from typing import List


class TokenContents(BaseModel):
    email: str
    roles: List[str]
