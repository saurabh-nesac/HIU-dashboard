import h5py
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timedelta

INPUT_DIR = Path(r"F:\Saurabh\dashboard\GPM")
OUTPUT_DIR = Path(r"F:\Saurabh\dashboard\GPM_hourly_bin")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_RAIN_RATE = 400  # mm/hr (upper physical bound)
EXPECTED_DELTA = timedelta(minutes=30)

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


def extract_time(filename):
    base = os.path.basename(filename)
    date = base.split('.')[4].split('-')[0]
    time = base.split('-S')[1][:6]
    return datetime.strptime(date + time, "%Y%m%d%H%M%S")


# --- SORT FILES ---
files = sorted(INPUT_DIR.glob("*.HDF5"), key=lambda x: extract_time(str(x)))

print(f"Total files found: {len(files)}")

# --- CHECK 30-MIN CONTINUITY ---
for i in range(len(files) - 1):
    t1 = extract_time(str(files[i]))
    t2 = extract_time(str(files[i + 1]))

    if (t2 - t1) != EXPECTED_DELTA:
        print(f"⚠️ Missing or irregular interval: {files[i]} → {files[i+1]}")


# --- PROCESS IN PAIRS ---
for i in range(0, len(files) - 1, 2):
    f1 = files[i]
    f2 = files[i + 1]

    t1 = extract_time(str(f1))
    t2 = extract_time(str(f2))

    # --- PAIR CHECK ---
    if (t2 - t1) != EXPECTED_DELTA:
        print(f"❌ Skipping bad pair: {f1}, {f2}")
        continue

    rain1, lat1, lon1 = read_imerg(f1)
    rain2, lat2, lon2 = read_imerg(f2)

    # --- SHAPE CHECK ---
    if rain1.shape != rain2.shape:
        print(f"❌ Shape mismatch: {f1}, {f2}")
        continue

    # --- VALUE CHECK ---
    def clean(rain, fname):
        invalid_mask = (
            (rain < 0) |
            (rain > MAX_RAIN_RATE) |
            np.isnan(rain)
        )

        if np.any(invalid_mask):
            print(f"⚠️ Bad values in {fname}: {np.sum(invalid_mask)} pixels")
            print(f"{rain}")
            rain[invalid_mask] = 0

        return rain

    rain1 = clean(rain1, f1.name)
    rain2 = clean(rain2, f2.name)

    # --- CONVERT TO HOURLY ---
    rain_hourly = (rain1 + rain2) * 0.5

    # --- FINAL SANITY CHECK ---
    if np.max(rain_hourly) > 200:
        print(f"⚠️ Extreme hourly rain (>200 mm): {f1}")

    # Flip latitude
    rain_hourly = np.flipud(rain_hourly)

    rain_hourly = rain_hourly.astype(np.float32)

    out_name = t1.strftime("%Y%m%d_%H00.bin")
    out_path = OUTPUT_DIR / out_name

    rain_hourly.tofile(out_path)

    print(f"✅ Saved: {out_name}")