import xarray as xr
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter
from rasterio.transform import from_bounds
from pathlib import Path

from rainfall_step import compute_rain_step
from colormap import rain_to_rgba

INPUT = r"F:\Saurabh\dashboard\wrfFrema\3km\FREMAA_2024060500Z.nc"
OUT = Path("data/rgba_tif")

OUT.mkdir(parents=True, exist_ok=True)

BLUR_SIGMA = 1.2

ds = xr.open_dataset(INPUT)

rain_all = ds["rain"].values
lat = ds["lat"].values
lon = ds["lon"].values

# Fix latitude orientation
flip_lat = False
if lat[0] > lat[-1]:
    lat = lat[::-1]
    flip_lat = True

print("Processing frames...")

for t in range(1, len(ds.time)):

    # 1. Time differencing
    frame = compute_rain_step(rain_all, t)

    # 2. Blur
    frame = gaussian_filter(frame, sigma=BLUR_SIGMA)

    # 3. Fix orientation
    if flip_lat:
        frame = np.flipud(frame)

    # 4. RGBA mapping
    rgba = rain_to_rgba(frame)

    height, width = frame.shape

    transform = from_bounds(
        lon.min(), lat.min(),
        lon.max(), lat.max(),
        width, height
    )

    out_file = OUT / f"rain_{t:03}.tif"

    with rasterio.open(
        out_file,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=4,
        dtype="uint8",
        crs="EPSG:4326",
        transform=transform
    ) as dst:
        dst.write(rgba)

    print(f"Saved: {out_file}")

print("Done.")