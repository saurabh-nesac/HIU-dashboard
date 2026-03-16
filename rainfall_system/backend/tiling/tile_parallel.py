import subprocess
import multiprocessing
from pathlib import Path

def build_tile(tif):

    out = Path("tiles") / tif.stem

    cmd = [
        "gdal2tiles.py",
        "-z","7-12",
        "-w","none",
        str(tif),
        str(out)
    ]

    subprocess.run(cmd)


def run_parallel(tif_files):

    with multiprocessing.Pool(4) as p:
        p.map(build_tile, tif_files)