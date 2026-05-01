import xarray as xr
import numpy as np
import json

# Load WRF output
ds = xr.open_dataset(r"rainfall_system\data\wrf_raw\wrfout_d02_2025-10-15_00_00_00", engine="netcdf4")

# VARIABLES (example)
rain = ds["RAINNC"]  # accumulated rain
lat = ds["XLAT"][0]
lon = ds["XLONG"][0]

# Target location
target_lat = 25.57
target_lon = 91.88

# Find nearest grid point
dist = (lat - target_lat)**2 + (lon - target_lon)**2
iy, ix = np.unravel_index(dist.argmin(), dist.shape)

# Extract time series
rain_series = rain[:, iy, ix].values

# Convert to incremental rainfall
rain_inc = np.diff(rain_series, prepend=rain_series[0])

# Time
times = ds["Times"].values

# Build JSON
data = []
for t, r in zip(times, rain_inc):
    data.append({
        "time": str(t),
        "rain": float(r)
    })

with open("meteogram.json", "w") as f:
    json.dump(data, f, indent=2)

print("Saved meteogram.json")