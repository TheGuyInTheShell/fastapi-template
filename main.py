try:
    from core.config.globals import settings
    import asyncio
    import os

    from app.sockets import init_sockets
    from core.plugins.base import plugin_manager


    import socketio

    from fastapi import FastAPI

    from fastapi.staticfiles import StaticFiles

    from fastapi.templating import Jinja2Templates

    from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

    from fastapi.openapi.utils import get_openapi

    from fastapi.responses import HTMLResponse

    from fastapi import Depends


    import core.jobs as jobs

    import core.middlewares as middlewares
    from admin.templates import init_admin

    from core.database import BaseAsync, BaseSync, SessionAsync, engineSync, get_async_db

    from core.routes import api_router, routes

    from core.services.init_auth import init_auth

    from starlette.responses import Response

    version = "1.0.0"

    mode = settings.MODE
    if mode != "DEVELOPMENT":
        docs_url = None
        redoc_url = None
        openapi_url = None
    else:
        docs_url = "/docs"
        redoc_url = "/redoc"
        openapi_url = "/openapi.json"


    app = FastAPI(
        title="FastAPI Template",
        version=version,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=plugin_manager.manage_lifespan,
    )


    @app.get(
        "/docs",
        include_in_schema=False,
        response_class=HTMLResponse,
        dependencies=[Depends(middlewares.role_verify_cookie.ROLE_VERIFY_COOKIE)],
    )
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=app.title + " - Docs",
        )


    @app.get(
        "/redoc",
        include_in_schema=False,
        response_class=HTMLResponse,
        dependencies=[Depends(middlewares.role_verify_cookie.ROLE_VERIFY_COOKIE)],
    )
    async def custom_redoc_html():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=app.title + " - Redoc",
        )


    @app.get(
        "/openapi.json",
        include_in_schema=False,
        dependencies=[Depends(middlewares.role_verify_cookie.ROLE_VERIFY_COOKIE)],
    )
    async def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        app.openapi_schema = openapi_schema
        return app.openapi_schema


    app = middlewares.initialazer(app)


    app = jobs.set_jobs(app)


    # Socket io (sio) create a Socket.IO server

    socket_app = init_sockets(app)
    app.mount("/sio", socket_app)


    app.mount("/public", StaticFiles(directory="app/public"))


    # Node modules

    app.mount("/node_modules", StaticFiles(directory="node_modules"), name="node_modules")


    # Static files

    app.mount("/static", StaticFiles(directory="admin/static"), name="admin")


    # Jinja2 templates for admin panel

    templates = Jinja2Templates(directory="admin/src")

    admin_routes = init_admin(templates, app)

    app.include_router(api_router)

    # Database initialization models (Deprecated in favor of Alembic)
    # BaseSync.metadata.create_all(engineSync)
    # BaseAsync.metadata.create_all(engineSync)


    asyncio.ensure_future(init_auth([*routes, *admin_routes], SessionAsync))


except Exception as e:
    print(e)
    os._exit(0)