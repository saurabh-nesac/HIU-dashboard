from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .rain_tiles import router

app = FastAPI()

app.include_router(router)

app.mount("/",StaticFiles(directory="frontend",html=True),name="frontend")