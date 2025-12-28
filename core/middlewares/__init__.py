from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .jwt_verify import JWT_VERIFY
from .role_verify import ROLE_VERIFY
from .prometheus import PrometheusMiddleware


def initialazer(app=FastAPI()):
    origins = [
        "*",  # Vue app
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add Prometheus metrics middleware
    app.add_middleware(PrometheusMiddleware)
    
    return app
