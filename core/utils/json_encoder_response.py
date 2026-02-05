from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def json_encoder_response(data: Any):
    return JSONResponse(content=jsonable_encoder(data), status_code=200)
