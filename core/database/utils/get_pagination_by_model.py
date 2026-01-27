from sqlalchemy import Select, select, desc
from database import BaseAsync, BaseSync
from typing import TypeVar, Union

# Define the TypeVar to represent the instance
T = TypeVar('T', bound=Union[BaseSync, BaseAsync])

def get_pagination_by_model(
    pag: int, 
    ord_dir: str,  # Renamed 'ord' to avoid confusion with the built-in ord()
    Model: type[T]  # Use type[T] because you are passing the class, not an instance
) -> Select[tuple[T]]: # Select expects a tuple representing the row shape
    offset = (pag - 1) * 10
    limit = 10
    
    if ord_dir == "DESC":
        query = select(Model).order_by(desc(Model.id)).offset(offset).limit(limit)
    else:
        query = select(Model).offset(offset).limit(limit)
        
    return query
