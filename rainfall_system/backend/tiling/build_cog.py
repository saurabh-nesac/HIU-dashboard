import subprocess
from pathlib import Path

INPUT = Path("data/rgba_tif")
OUT = Path("data/cog")

OUT.mkdir(exist_ok=True)

for tif in INPUT.glob("*.tif"):

    out = OUT / tif.name

    print("Building COG:",tif.name)

    subprocess.run([
        "gdal_translate",
        str(tif),
        str(out),
        "-of","COG",
        "-co","COMPRESS=LZW"
    ],check=True)

    subprocess.run([
        "gdaladdo",
        "-r","average",
        str(out),
        "2","4","8","16","32"
    ])