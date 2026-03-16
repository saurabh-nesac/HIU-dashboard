import json
from pathlib import Path

tiles = Path("tiles")

timestamps = sorted([p.name for p in tiles.iterdir()])

with open("config/manifest.json","w") as f:

    json.dump({"timestamps":timestamps}, f)