from fastapi import APIRouter
from routes import users

api_router = APIRouter()

@api_router.get('/')
def response():
    return {"result": "Ok!"}

routes = [
    {
    "router": users.router,
    "prefix": "/users"
    },
]

for route in routes:
    api_router.include_router(router=route["router"], prefix=route["prefix"])
