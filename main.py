from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import api_router
import middlewares
import jobs

app = FastAPI()

app = middlewares.initialazer(app)
app = jobs.set_jobs(app)

app.mount('/static', StaticFiles(directory='public'))

app.include_router(api_router)