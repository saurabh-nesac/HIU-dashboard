import xarray as xr
import numpy as np
from scipy.ndimage import gaussian_filter
from pathlib import Path
import pandas as pd
import json

INPUT = r"wrfFrema\3km\FREMAA_2025101500Z.nc"
OUT = Path("data/bin")

OUT.mkdir(parents=True, exist_ok=True)

BLUR_SIGMA = 0.3

lat0 = 26.1445 #guwahati
lon0 = 91.7362

ds = xr.open_dataset(INPUT)


time_values = ds["time"].values
# Convert to datetime
time_stamps = pd.to_datetime(time_values).to_pydatetime()

time_strings = [t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in time_stamps]

# find nearest indices
lat_arr = ds["lat"].values
lon_arr = ds["lon"].values

iy = np.abs(lat_arr - lat0).argmin()
ix = np.abs(lon_arr - lon0).argmin()

print("Nearest grid point:")
print("lat:", lat_arr[iy], "lon:", lon_arr[ix])

  
rain_series = ds['rain'][:, iy, ix].values
rain_hourly = np.diff(rain_series)
# rain_hourly = rain_series

rain_hourly[rain_hourly < 0] = 0

for t, val in enumerate(rain_hourly, start=1):
    print(f"t={t:02} → {val:.2f} mm/hr")

rain_all = ds["rain"].values  # (t, lat, lon)

lat = ds["lat"].values
lon = ds["lon"].values

height = len(lat)
width = len(lon)

print("Exporting binary frames...")

cumulative = np.zeros_like(rain_all[0])
global_max = 0

for t in range(1, len(ds.time)):

    frame = rain_all[t] - rain_all[t-1]
    frame_times = time_strings[1:]
    frame[frame < 0] = 0

    # frame = gaussian_filter(frame, sigma=BLUR_SIGMA)

    # 👉 accumulate
    cumulative += frame

    # 👉 compute max for this timestep
    frame_max = frame.max()
    cum_max = cumulative.max()

    global_max = max(global_max, cum_max)

    print(f"Frame {t:02} → step max: {frame_max:.2f} mm | cumulative max: {cum_max:.2f} mm")

    # save frame (unchanged)
    frame = frame.astype("float32")
    out_file = OUT / f"rain_{t:03}.bin"
    frame.tofile(out_file)
    
    # Save metadata
    meta = {
        "width": width,
        "height": height,
        "frames": len(ds.time) - 1,
        "bbox": [
            float(lon.min()),
            float(lat.min()),
            float(lon.max()),
            float(lat.max())
        ],
        "timestamps": frame_times,
        "lat": lat.tolist(),
        "lon": lon.tolist(),
        "nx": len(lon),
        "ny": len(lat),
    }

    with open(OUT / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("Done.")