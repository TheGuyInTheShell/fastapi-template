from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def json_encoder_response(data: any):
    return JSONResponse(content=jsonable_encoder(data), status_code=200) 
