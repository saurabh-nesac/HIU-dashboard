from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/tiles", StaticFiles(directory="tiles"), name="tiles")

@app.get("/manifest")
def get_manifest():
    import json
    with open("config/manifest.json") as f:
        return json.load(f)