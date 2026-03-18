import subprocess
import multiprocessing
from pathlib import Path

TIF_DIR = Path("data/rgba_tif")
OUT_DIR = Path("tiles")


def build_tile(tif):

    out = OUT_DIR / tif.stem
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "gdal2tiles.py",
        "--processes=4",
        "-z","7-12",
        "-w","none",
        str(tif),
        str(out)
    ]

    print(f"Generating tiles for {tif.name}")

    subprocess.run(cmd, check=True)


def run_parallel(tif_files):

    with multiprocessing.Pool(processes=4) as pool:
        pool.map(build_tile, tif_files)


if __name__ == "__main__":

    tif_files = sorted(TIF_DIR.glob("*.tif"))

    print(f"Found {len(tif_files)} tif files")

    run_parallel(tif_files)

    print("Tile generation complete")