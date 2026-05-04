import json
import h5py
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timedelta

INPUT_DIR = Path(r"F:\Saurabh\dashboard\GPM")
OUTPUT_DIR = Path(r"F:\Saurabh\dashboard\GPM_hourly_bin")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_RAIN_RATE = 400  # mm/hr
EXPECTED_DELTA = timedelta(minutes=30)

# ================================
# READ IMERG
# ================================
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
# EXTRACT TIME
# ================================
def extract_time(filename):
    base = os.path.basename(filename)
    date = base.split('.')[4].split('-')[0]
    time = base.split('-S')[1][:6]
    return datetime.strptime(date + time, "%Y%m%d%H%M%S")


# ================================
# CLEAN DATA
# ================================
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


# ================================
# LOAD FILES
# ================================
files = sorted(INPUT_DIR.glob("*.HDF5"), key=lambda x: extract_time(str(x)))

print(f"Total files found: {len(files)}")

if len(files) < 2:
    raise ValueError("❌ Not enough files")

if len(files) % 2 != 0:
    print("⚠️ Odd number of files, last file ignored")


# ================================
# CHECK CONTINUITY
# ================================
for i in range(len(files) - 1):
    t1 = extract_time(str(files[i]))
    t2 = extract_time(str(files[i + 1]))

    if (t2 - t1) != EXPECTED_DELTA:
        print(f"⚠️ Missing interval: {files[i]} → {files[i+1]}")


# ================================
# PROCESS
# ================================
timestamps = []
LAT = None
LON = None

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
    # FIX ORIENTATION (CRITICAL)
    # ================================
    if rain1.shape == (len(lon1), len(lat1)):
        print("🔄 Transposing IMERG grid (lon,lat → lat,lon)")
        rain1 = rain1.T
        rain2 = rain2.T

    # ================================
    # GRID CHECK
    # ================================
    if not (np.array_equal(lat1, lat2) and np.array_equal(lon1, lon2)):
        print(f"❌ Grid mismatch: {f1}, {f2}")
        continue

    if rain1.shape != rain2.shape:
        print(f"❌ Shape mismatch: {f1}, {f2}")
        continue

    # ================================
    # CLEAN
    # ================================
    rain1 = clean(rain1, f1.name)
    rain2 = clean(rain2, f2.name)
    
    print("Rain shape:", rain1.shape)
    print("Lat size:", len(lat1))
    print("Lon size:", len(lon1))

    # ================================
    # HOURLY CONVERSION
    # ================================
    rain_hourly = (rain1 + rain2) * 0.5

    if np.max(rain_hourly) > 200:
        print(f"⚠️ Extreme rainfall detected: {f1}")

    # ================================
    # SUBSET (NE INDIA DOMAIN)
    # ================================
    lat_mask = (lat1 >= 19.35) & (lat1 <= 30.66)
    lon_mask = (lon1 >= 87.32) & (lon1 <= 99.03)

    # apply correctly
    rain_hourly = rain_hourly[lat_mask, :][:, lon_mask]

    lat_sub = lat1[lat_mask]
    lon_sub = lon1[lon_mask]

    # ================================
    # FLIP LAT (match frontend)
    # ================================
    rain_hourly = np.flipud(rain_hourly).astype(np.float32)

    # ================================
    # STORE META (ONCE)
    # ================================
    if LAT is None:
        LAT = lat_sub[::-1].tolist()   # flipped
        LON = lon_sub.tolist()

    # ================================
    # SAVE BIN
    # ================================
    frame_idx = len(timestamps) + 1
    out_name = f"rain_{frame_idx:03d}.bin"
    out_path = OUTPUT_DIR / out_name

    rain_hourly.tofile(out_path)

    print(f"✅ Saved: {out_name} | Shape: {rain_hourly.shape}")

    # ================================
    # TIMESTAMP (MIDPOINT)
    # ================================
    mid_time = t1 + (t2 - t1) / 2
    timestamps.append(mid_time.isoformat())


# ================================
# SAVE META.JSON
# ================================
meta = {
    "lat": LAT,
    "lon": LON,
    "timestamps": timestamps,
    "nx": len(LON),
    "ny": len(LAT),
    "source": "GPM_IMERG",
    "interval_minutes": 60
}

meta_path = OUTPUT_DIR / "meta.json"

with open(meta_path, "w") as f:
    json.dump(meta, f)

print(f"\n✅ meta.json saved → {meta_path}")