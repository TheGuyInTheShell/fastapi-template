# RQ -> request
# RS -> response
# IN -> internal
from typing import Any, Dict, Literal

from pydantic import BaseModel


class SearchParams(BaseModel):
    query: Dict[Literal["eq", "bt", "ne"], str] = {}
