import os


async def delete_file(path: str):
    os.remove(path)