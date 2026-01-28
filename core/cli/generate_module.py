"""
CLI module generator for creating FastAPI module structures.
"""
import os
from pathlib import Path
from typing import List


def get_module_path_parts(module_name: str) -> List[str]:
    """
    Convert module name (e.g., 'module1.module2') to path parts.
    
    Args:
        module_name: Module name with dots as separators
        
    Returns:
        List of path parts
    """
    return module_name.split('.')


def create_controller_template(module_name: str) -> str:
    """Generate controller.py template"""
    tag = module_name.split('.')[-1]  # Get last part for tag
    
    return f'''from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import {tag.capitalize()}
from .schemas import (
    RQ{tag.capitalize()},
    RS{tag.capitalize()},
    RS{tag.capitalize()}List,
)

# prefix /{tag}
router = APIRouter()

tag = "{tag}"


@router.get("/id/{{id}}", response_model=RS{tag.capitalize()}, status_code=200, tags=[tag])
async def get_{tag}(
    id: str, db: AsyncSession = Depends(get_async_db)
) -> RS{tag.capitalize()}:
    try:
        result = await {tag.capitalize()}.find_one(db, id)
        return RS{tag.capitalize()}(
            uid=result.uid,
            # Add additional fields here
        )
    except Exception as e:
        print(e)
        raise e


@router.get("/", response_model=RS{tag.capitalize()}List, status_code=200, tags=[tag])
async def get_{tag}s(
    pag: Optional[int] = 1,
    ord: Literal["asc", "desc"] = "asc",
    status: Literal["deleted", "exists", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RS{tag.capitalize()}List:
    try:
        result = await {tag.capitalize()}.find_some(db, pag or 1, ord, status)
        result2 = list(map(
            lambda x: RS{tag.capitalize()}(
                uid=x.uid,
                # Add additional fields here
            ),
            result,
        ))
        return RS{tag.capitalize()}List(
            data=result2,
            total=0,
            page=0,
            page_size=0,
            total_pages=0,
            has_next=False,
            has_prev=False,
            next_page=0,
            prev_page=0,
        )
    except Exception as e:
        print(e)
        raise e


@router.post("/", response_model=RS{tag.capitalize()}, status_code=201, tags=[tag])
async def create_{tag}(
    {tag}: RQ{tag.capitalize()}, db: AsyncSession = Depends(get_async_db)
) -> RS{tag.capitalize()}:
    try:
        result = await {tag.capitalize()}(**{tag}.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete("/id/{{id}}", status_code=204, tags=[tag])
async def delete_{tag}(id: str, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await {tag.capitalize()}.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put("/id/{{id}}", response_model=RS{tag.capitalize()}, status_code=200, tags=[tag])
async def update_{tag}(
    id: str, {tag}: RQ{tag.capitalize()}, db: AsyncSession = Depends(get_async_db)
) -> RS{tag.capitalize()}:
    try:
        result = await {tag.capitalize()}.update(db, id, {tag}.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e
'''


def create_schemas_template(module_name: str) -> str:
    """Generate schemas.py template"""
    tag = module_name.split('.')[-1]
    
    return f'''from typing import List
from pydantic import BaseModel


class RQ{tag.capitalize()}(BaseModel):
    """Request schema for creating/updating {tag}"""
    name: str
    description: str


class RS{tag.capitalize()}(BaseModel):
    """Response schema for {tag}"""
    uid: str
    name: str
    description: str


class RS{tag.capitalize()}List(BaseModel):
    """Response schema for list of {tag}s"""
    data: list[RS{tag.capitalize()}] | List = []
    total: int = 0
    page: int | None = 0
    page_size: int | None = 0
    total_pages: int | None = 0
    has_next: bool | None = False
    has_prev: bool | None = False
    next_page: int | None = 0
    prev_page: int | None = 0
'''


def create_models_template(module_name: str) -> str:
    """Generate models.py template"""
    tag = module_name.split('.')[-1]
    table_name = tag.lower() + 's'
    
    return f'''from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import BaseAsync


class {tag.capitalize()}(BaseAsync):
    __tablename__ = "{table_name}"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
'''


def create_services_template(module_name: str) -> str:
    """Generate services.py template"""
    tag = module_name.split('.')[-1]
    
    return f'''from sqlalchemy.ext.asyncio import AsyncSession

from .models import {tag.capitalize()}


async def create_{tag}(
    db: AsyncSession,
    name: str,
    description: str
) -> {tag.capitalize()}:
    """
    Create a new {tag} in the database.
    
    Args:
        db: Database session
        name: Name of the {tag}
        description: Description of the {tag}
        
    Returns:
        {tag.capitalize()}: The created {tag}
    """
    {tag}_obj = {tag.capitalize()}(
        name=name,
        description=description,
    )
    await {tag}_obj.save(db)
    return {tag}_obj
'''


def create_init_template() -> str:
    """Generate __init__.py template"""
    return """# Module initialization
"""


def generate_module(module_name: str, base_path: Path | None = None):
    """
    Generate a complete module structure with controller, schemas, models, and services.
    
    Args:
        module_name: Name of the module (supports nested with dots, e.g., 'module1.module2')
        base_path: Base path for modules (default: app/modules)
    """
    if base_path is None:
        # Get the project root (assuming this script is in core/cli/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        base_path = project_root / "app" / "modules"
    else:
        base_path = Path(base_path)
    
    # Get path parts (e.g., ['module1', 'module2'])
    path_parts = get_module_path_parts(module_name)
    
    # Create full path
    module_path = base_path
    for part in path_parts:
        module_path = module_path / part
    
    # Create directory structure
    module_path.mkdir(parents=True, exist_ok=True)
    print(f"[+] Created directory: {module_path}")
    
    # Create __init__.py files for each level
    current_path = base_path
    for part in path_parts:
        current_path = current_path / part
        init_file = current_path / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(create_init_template())
            print(f"[OK] Created: {init_file.relative_to(base_path.parent.parent)}")
    
    # Create module files
    files = {
        'controller.py': create_controller_template(module_name),
        'schemas.py': create_schemas_template(module_name),
        'models.py': create_models_template(module_name),
        'services.py': create_services_template(module_name),
    }
    
    for filename, content in files.items():
        file_path = module_path / filename
        if file_path.exists():
            print(f"[SKIP] Already exists: {file_path.relative_to(base_path.parent.parent)}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Created: {file_path.relative_to(base_path.parent.parent)}")
    
    print(f"\n[SUCCESS] Module '{module_name}' generated successfully!")
    print(f"[INFO] Location: {module_path}")
    print(f"\n[HINT] Next steps:")
    print(f"   1. Review and customize the generated files")
    print(f"   2. Add the router to your main application")
    print(f"   3. Run migrations if you modified the models")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m core.cli.generate_module <module_name>")
        print("Example: python -m core.cli.generate_module products")
        print("Example (nested): python -m core.cli.generate_module store.products")
        sys.exit(1)
    
    module_name = sys.argv[1]
    generate_module(module_name)
