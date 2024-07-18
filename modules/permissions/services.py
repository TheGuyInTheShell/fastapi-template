from typing import List

from fastapi.routing import APIRoute, BaseRoute
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Permission


async def create_permissions_api(routes: List[BaseRoute], sessionAsync):
        db: AsyncSession = sessionAsync()
        try:
            for route in routes:
                if isinstance(route, APIRoute):
                    try:
                        permission = await Permission.find_by_colunm(db, 'name', route.name)
                        result = permission.scalar_one_or_none()
                        name: str = route.__getattribute__('name')
                        methods: set = route.__getattribute__('methods')
                        description: str = route.__getattribute__('path')
                        if result is None:
                            await Permission(name=name, 
                                             action=next(iter(methods)),
                                             description=description,
                                             type='API'
                                             ).save(db)
                    except Exception as e:
                        print(e)
                        continue    
        except Exception as e:
             print(e)
        finally:
            await db.close()