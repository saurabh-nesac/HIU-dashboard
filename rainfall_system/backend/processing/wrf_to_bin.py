import xarray as xr
import numpy as np
from scipy.ndimage import gaussian_filter
from pathlib import Path

INPUT = r"F:\Saurabh\dashboard\wrfFrema\3km\FREMAA_2024060500Z.nc"
OUT = Path("data/bin")

OUT.mkdir(parents=True, exist_ok=True)

BLUR_SIGMA = 1.2

ds = xr.open_dataset(INPUT)

rain_all = ds["rain"].values  # (t, lat, lon)

lat = ds["lat"].values
lon = ds["lon"].values

height = len(lat)
width = len(lon)

print("Exporting binary frames...")

for t in range(1, len(ds.time)):

    frame = rain_all[t] - rain_all[t-1]
    frame[frame < 0] = 0

    frame = gaussian_filter(frame, sigma=BLUR_SIGMA)

    # normalize (important for GPU)
    frame = np.clip(frame, 0, 50) / 50.0

    # convert to float32
    frame = frame.astype("float32")

    out_file = OUT / f"rain_{t:03}.bin"
    frame.tofile(out_file)

    print("Saved:", out_file)

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
    ]
}

import json
with open(OUT / "meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("Done.")