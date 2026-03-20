from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# backend/api/main.py → go 3 levels up → rainfall_system

DATA_DIR = BASE_DIR / "data"
TILES_DIR = BASE_DIR / "tiles"

app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")
app.mount("/tiles", StaticFiles(directory=str(TILES_DIR)), name="tiles")

@app.get("/manifest")
def get_manifest():
    import json
    with open(BASE_DIR / "config" / "manifest.json") as f:
        return json.load(f)