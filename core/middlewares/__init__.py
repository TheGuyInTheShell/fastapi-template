from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .jwt_verify import JWT_VERIFY
from .role_verify import ROLE_VERIFY


def initialazer(app = FastAPI()):
    origins = [
        "*",   # Vue app
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app