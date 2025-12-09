from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

class InitTemplate:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.router = APIRouter()

    def add_page(self):
        @self.router.get("", response_class=HTMLResponse)
        async def modules_page(request: Request):

            """
            [Route(path='/openapi.json', name='openapi', methods=['GET', 'HEAD']), Route(path='/docs', name='swagger_ui_html', methods=['GET', 'HEAD']), Route(path='/docs/oauth2-redirect', name='swagger_ui_redirect', methods=['GET', 'HEAD']), Route(path='/redoc', name='redoc_html', methods=['GET', 'HEAD']), Mount(path='/sio', name='', app=<socketio.asgi.ASGIApp object at 0x00000236C7004710>), Mount(path='/public', name='', app=<starlette.staticfiles.StaticFiles object at 0x00000236C80C1940>), Mount(path='/node_modules', name='node_modules', app=<starlette.staticfiles.StaticFiles object at 0x00000236C80C18E0>), Mount(path='/static', name='admin', app=<starlette.staticfiles.StaticFiles object at 0x00000236C80C1FD0>), APIRoute(path='/favicon.ico', name='favicon', methods=['GET']), APIRoute(path='/admin/api-tokens', name='main_api_tokens', methods=['GET']), APIRoute(path='/admin/api-tokens/partial/info', name='read_info', methods=['GET']), APIRoute(path='/admin/dashboard', name='main_dashboard', methods=['GET']), APIRoute(path='/admin/dashboard/partial/info', name='read_info', methods=['GET']), APIRoute(path='/admin/models', name='models_diagram_page', methods=['GET']), APIRoute(path='/admin/modules', name='modules_page', methods=['GET']), APIRoute(path='/admin/roles', name='roles_page', methods=['GET']), APIRoute(path='/admin/roles/create', name='create_role_page', methods=['GET']), APIRoute(path='/admin/roles/create', name='create_role', methods=['POST']), APIRoute(path='/admin/roles/edit/{role_id}', name='edit_role_page', methods=['GET']), APIRoute(path='/admin/roles/edit/{role_id}', name='edit_role', methods=['POST']), APIRoute(path='/admin/roles/partial/delete/{role_id}', name='delete_role', methods=['DELETE']), APIRoute(path='/admin/sign-in', name='main_sign_in', methods=['GET']), APIRoute(path='/admin/sign-in/partial/sign-in', name='sign_in', methods=['POST']), APIRoute(path='/admin/users', name='users_page', methods=['GET']), APIRoute(path='/check', name='response', methods=['GET']), APIRoute(path='/auth/', name='token', methods=['GET']), APIRoute(path='/auth/sign-in', name='sign_in', methods=['POST']), APIRoute(path='/auth/sign-up', name='sign_up', methods=['POST']), APIRoute(path='/menu/id/{id}', name='get_Permission', methods=['GET']), APIRoute(path='/menu/', name='get_Permissions', methods=['GET']), APIRoute(path='/menu/', name='create_Permission', methods=['POST']), APIRoute(path='/menu/id/{id}', name='delete_Permission', methods=['DELETE']), APIRoute(path='/menu/id/{id}', name='update_Permission', methods=['PUT']), APIRoute(path='/menu/roleid/{id}', name='get_Permission', methods=['GET']), APIRoute(path='/menu/role/', name='get_Permissions', methods=['GET']), APIRoute(path='/menu/role/', name='create_Permission', methods=['POST']), APIRoute(path='/menu/roleid/{id}', name='delete_Permission', methods=['DELETE']), APIRoute(path='/menu/roleid/{id}', name='update_Permission', methods=['PUT']), APIRoute(path='/permissions/id/{id}', name='get_Permission', methods=['GET']), APIRoute(path='/permissions/', name='get_Permissions', methods=['GET']), APIRoute(path='/permissions/all', name='get_all_Permissions', methods=['GET']), APIRoute(path='/permissions/', name='create_Permission', methods=['POST']), APIRoute(path='/permissions/id/{id}', name='delete_Permission', methods=['DELETE']), APIRoute(path='/permissions/id/{id}', name='update_Permission', methods=['PUT']), APIRoute(path='/roles/id/{id}', name='get_Role', methods=['GET']), APIRoute(path='/roles/', name='get_Roles', methods=['GET']), APIRoute(path='/roles/', name='create_Role', methods=['POST']), APIRoute(path='/roles/id/{id}', name='delete_Role', methods=['DELETE']), APIRoute(path='/roles/id/{id}', name='update_Role', methods=['PUT']), APIRoute(path='/role_permissions/role/{role_id}', name='get_role_permissions_endpoint', methods=['GET']), APIRoute(path='/role_permissions/assign', name='assign_permission', methods=['POST']), APIRoute(path='/role_permissions/remove', name='remove_permission', methods=['POST']), APIRoute(path='/tokens/id/{id}', name='get_token', methods=['GET']), APIRoute(path='/tokens/', name='get_tokens', methods=['GET']), APIRoute(path='/tokens/id/{id}', name='delete_tokens', methods=['DELETE']), APIRoute(path='/tokens/', name='create_token', methods=['POST']), APIRoute(path='
            """
            routes = request.app.routes
            
            
            modules = []
            # Process defined
            for route in routes:
                try:
                    name: str = route.__getattribute__('name')
                    methods: set = route.__getattribute__('methods')
                    description: str = route.__getattribute__('path')
                    modules.append({
                            "name": name,
                            "methods": methods,
                            "description": description
                        })
                    print(name, methods, description)
                except Exception as e:
                    print(e)
                    continue    
            
            return self.templates.TemplateResponse(
                "pages/modules.html",
                context={
                    "request": request,
                    "modules": modules,
                },
            )

    def add_all(self):
        self.add_page()
        return self.router
