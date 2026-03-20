from fastapi import APIRouter
from fastapi.responses import Response
from rio_tiler.io import COGReader
from rio_tiler.errors import TileOutsideBounds
from pathlib import Path
from functools import lru_cache

router = APIRouter()

DATA = Path("data/cog")


EMPTY_TILE = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'


# ------------------------------------------------
# TILE CACHE
# ------------------------------------------------
@lru_cache(maxsize=5000)
def get_tile(frame: int, z: int, x: int, y: int):

    tif = DATA / f"rain_{frame:03}.tif"

    try:
        with COGReader(input=str(tif), options={"nodata": 0}) as cog:
            img = cog.tile(x, y, z)

        return img.render(img_format="PNG")

    except TileOutsideBounds:
        return EMPTY_TILE
# ------------------------------------------------
# API ENDPOINT
# ------------------------------------------------

@router.get("/rain/{frame}/{z}/{x}/{y}.png")
def rain_tile(frame: int, z: int, x: int, y: int):

    tile = get_tile(frame, z, x, y)

    return Response(
        content=tile,
        media_type="image/png"
    )
    
@router.get("/cache")
def cache_info():
    return get_tile.cache_info()._asdict()