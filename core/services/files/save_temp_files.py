import tempfile
from typing import Callable


async def save_temp_files(file: any, callback: Callable[[str], any]):
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        data = await file.read()
        temp.write(data)
        temp_path = temp.name
        return await callback(temp_path)