import xarray as xr
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter
from rasterio.transform import from_bounds
from pathlib import Path

INPUT = r"F:\Saurabh\dashboard\rainfall_system\data\wrf_raw\wrfout_d02_2025-10-15_00_00_00"
OUT = Path("data/rgba_tif")

OUT.mkdir(exist_ok=True)

ds = xr.open_dataset(INPUT)

rainc = ds["RAINC"]
rainnc = ds["RAINNC"]

lat = ds["XLAT"][0].values
lon = ds["XLONG"][0].values


def rain_to_rgba(rain):

    rain = np.clip(rain,0,80)

    r = np.zeros_like(rain)
    g = rain * 2
    b = rain * 4

    a = np.where(rain>0.1,180,0)

    rgba = np.stack([r,g,b,a],axis=0)

    return rgba.astype("uint8")


for t in range(1,len(ds.Time)):

    rain = (
        rainc.isel(Time=t)+rainnc.isel(Time=t)
        -
        rainc.isel(Time=t-1)-rainnc.isel(Time=t-1)
    )

    rain = rain.values

    rain[rain<0] = 0

    rain = gaussian_filter(rain,1.3)

    rgba = rain_to_rgba(rain)

    height,width = rain.shape

    transform = from_bounds(
        lon.min(),
        lat.min(),
        lon.max(),
        lat.max(),
        width,
        height
    )

    out = OUT / f"rain_{t:03}.tif"

    with rasterio.open(
        out,
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

    print("Saved",out)