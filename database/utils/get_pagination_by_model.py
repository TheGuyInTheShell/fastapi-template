from sqlalchemy import select, desc
from database import BaseAsync, BaseSync

async def get_pagination_by_model(pag: int, ord: int, Model: BaseAsync | BaseSync) -> str:
    offset = (pag - 1)*10
    limit = 10
    if ord == 'DESC': 
        query = select(Model).order_by(desc(Model.id)).offset(offset).limit(limit)
    else:
        query = select(Model).offset(offset).limit(limit)
    return await query
