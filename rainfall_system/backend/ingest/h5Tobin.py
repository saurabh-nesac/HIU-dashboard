import json
import h5py
import numpy as np
import os

from pathlib import Path
from datetime import datetime, timedelta

import xarray as xr
import xesmf as xe

from skimage import measure
# ================================
# PATHS
# ================================
INPUT_DIR = Path(r"F:\Saurabh\dashboard\GPM")
OUTPUT_DIR = Path(r"F:\Saurabh\dashboard\GPM_hourly_bin")
WRF_META_PATH = Path(r"F:\Saurabh\dashboard\data\bin\meta.json")
WEIGHTS_PATH = Path(r"F:\Saurabh\dashboard\gpm_to_wrf_weights.nc")

OUTPUT_DIR.mkdir(exist_ok=True)

MAX_RAIN_RATE = 400
EXPECTED_DELTA = timedelta(minutes=30)

CONTOUR_LEVELS = [1, 5, 10, 20, 50, 100]

def generate_contours(data, levels, lat, lon):

    features = []

    for level in levels:

        contours = measure.find_contours(data, level)

        for contour in contours:

            coords = []

            for y, x in contour:

                lat_val = np.interp(
                    y,
                    np.arange(len(lat)),
                    lat
                )

                lon_val = np.interp(
                    x,
                    np.arange(len(lon)),
                    lon
                )

                coords.append([
                    float(lon_val),
                    float(lat_val)
                ])

            # skip tiny contours
            if len(coords) < 5:
                continue

            features.append({
                "type": "Feature",
                "properties": {
                    "value": float(level)
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }

# ================================
# LOAD WRF GRID (TARGET GRID)
# ================================
with open(WRF_META_PATH) as f:
    wrf_meta = json.load(f)

wrf_lat = np.array(wrf_meta["lat"])
wrf_lon = np.array(wrf_meta["lon"])

# ensure ascending latitude (required for xESMF)
if wrf_lat[0] > wrf_lat[-1]:
    wrf_lat = wrf_lat[::-1]

wrf_grid = xr.Dataset({
    "lat": (["lat"], wrf_lat),
    "lon": (["lon"], wrf_lon)
})

print("✅ WRF grid loaded:", (len(wrf_lat), len(wrf_lon)))

# ================================
# HELPERS
# ================================
def extract_time(filename):
    base = os.path.basename(filename)
    date = base.split('.')[4].split('-')[0]
    time = base.split('-S')[1][:6]
    return datetime.strptime(date + time, "%Y%m%d%H%M%S")

def clean(rain, fname):
    invalid_mask = (
        (rain < 0) |
        (rain > MAX_RAIN_RATE) |
        np.isnan(rain)
    )
    if np.any(invalid_mask):
        print(f"⚠️ Bad values in {fname}: {np.sum(invalid_mask)} pixels")
        rain[invalid_mask] = 0
    return rain

def read_imerg(file):
    with h5py.File(file, 'r') as f:
        grid = f['/Grid']

        if 'precipitationCal' in grid:
            rain = grid['precipitationCal'][:]
            source = "Final"
        elif 'precipitation' in grid:
            rain = grid['precipitation'][:]
            source = "Late/Early"
        else:
            raise ValueError(f"No valid precipitation variable in {file}")

        lat = grid['lat'][:]
        lon = grid['lon'][:]

    print(f"{os.path.basename(file)} → using {source}")
    return rain[0], lat, lon

# ================================
# LOAD FILES
# ================================
files = sorted(INPUT_DIR.glob("*.HDF5"), key=lambda x: extract_time(str(x)))
print(f"Total files found: {len(files)}")

if len(files) < 2:
    raise ValueError("❌ Not enough files")

if len(files) % 2 != 0:
    print("⚠️ Odd number of files, last file ignored")

# continuity check
for i in range(len(files) - 1):
    t1 = extract_time(str(files[i]))
    t2 = extract_time(str(files[i + 1]))
    if (t2 - t1) != EXPECTED_DELTA:
        print(f"⚠️ Missing interval: {files[i]} → {files[i+1]}")

# ================================
# MAIN PROCESS
# ================================
timestamps = []
regridder = None

for i in range(0, len(files) - 1, 2):

    f1 = files[i]
    f2 = files[i + 1]

    t1 = extract_time(str(f1))
    t2 = extract_time(str(f2))

    if (t2 - t1) != EXPECTED_DELTA:
        print(f"❌ Skipping bad pair: {f1}, {f2}")
        continue

    rain1, lat1, lon1 = read_imerg(f1)
    rain2, lat2, lon2 = read_imerg(f2)

    # ================================
    # FIX ORIENTATION
    # ================================
    if rain1.shape == (len(lon1), len(lat1)):
        print("🔄 Transposing IMERG grid")
        rain1 = rain1.T
        rain2 = rain2.T

    # ensure lat ascending
    if lat1[0] > lat1[-1]:   
        lat1 = lat1[::-1]
        rain1 = rain1[::-1, :]
        rain2 = rain2[::-1, :]

    # grid consistency
    if not (np.array_equal(lat1, lat2) and np.array_equal(lon1, lon2)):
        print(f"❌ Grid mismatch: {f1}, {f2}")
        continue

    # clean
    rain1 = clean(rain1, f1.name)
    rain2 = clean(rain2, f2.name)

    # ================================
    # HOURLY AVERAGE
    # ================================
    rain_hourly = (rain1 + rain2) * 0.5

    # ================================
    # CREATE REGRIDDER (ONCE)
    # ================================
    if regridder is None:
        gpm_grid = xr.Dataset({
            "lat": (["lat"], lat1),
            "lon": (["lon"], lon1)
        })

        regridder = xe.Regridder(
            gpm_grid,
            wrf_grid,
            method="bilinear",
            filename=str(WEIGHTS_PATH),
            reuse_weights=WEIGHTS_PATH.exists()
        )

        print("✅ xESMF regridder ready")

    # ================================
    # REGRID
    # ================================
    gpm_da = xr.DataArray(
        rain_hourly,
        dims=["lat", "lon"],
        coords={"lat": lat1, "lon": lon1}
    )

    rain_hourly = np.ascontiguousarray(
        regridder(gpm_da).values.astype(np.float32)
    )
    print("✅ Regridded shape:", rain_hourly.shape)

    # ================================
    # SAVE BIN
    # ================================
    frame_idx = len(timestamps) + 1
    out_name = f"rain_{frame_idx:03d}.bin"
    out_path = OUTPUT_DIR / out_name

    rain_hourly.tofile(out_path)
    # ================================
    # GENERATE CONTOURS
    # ================================
    geojson = generate_contours(
        rain_hourly,
        CONTOUR_LEVELS,
        wrf_lat,
        wrf_lon
    )

    contour_path = OUTPUT_DIR / f"contour_{frame_idx:03d}.geojson"

    with open(contour_path, "w") as f:
        json.dump(geojson, f)

    print(f"✅ Contours saved: contour_{frame_idx:03d}.geojson")

    print(f"✅ Saved: {out_name}")

    # ================================
    # TIMESTAMP (MIDPOINT)
    # ================================
    mid_time = t1 + (t2 - t1) / 2
    timestamps.append(mid_time.isoformat())

# ================================
# SAVE META.JSON (WRF GRID)
# ================================
meta = {
    "lat": wrf_lat.tolist(),
    "lon": wrf_lon.tolist(),
    "timestamps": timestamps,
    "nx": len(wrf_lon),
    "ny": len(wrf_lat),
    "source": "GPM_IMERG_REGRIDDED_XESMF",
    "interval_minutes": 60
}

meta_path = OUTPUT_DIR / "meta.json"

with open(meta_path, "w") as f:
    json.dump(meta, f)

print(f"\n✅ meta.json saved → {meta_path}")