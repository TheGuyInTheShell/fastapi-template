# from fastapi import UploadFile
# from database import Base
# from sqlalchemy.ext.asyncio import AsyncSession

# async def save_images(images: list[UploadFile], EmployeePhoto: Base, db: AsyncSession) -> None:
#         try:
#             for image in images:
#                 _, filename = await save_files(image)
#                 db.add(EmployeePhoto(
#                     imagen=filename,
#                     empleado=id
#                 ))     
#         except ValueError as err:
#             print(err)
#             return