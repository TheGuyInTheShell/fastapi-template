import tempfile
from typing import Any, Callable


async def save_temp_files(file: Any, callback: Callable[[str], Any]):
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        data = await file.read()
        temp.write(data)
        temp_path = temp.name
        return await callback(temp_path)
