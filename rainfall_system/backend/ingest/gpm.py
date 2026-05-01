import earthaccess
import os

# Login
# auth = earthaccess.login()
auth = earthaccess.login(strategy="interactive", persist=False)
print("Auth:", auth.authenticated)
# Date range (end is exclusive → include May 1)
date_range = ("2025-10-15", "2025-10-18")

# NE India bbox (optimized for WRF domain)
bbox = (88.0, 24.0, 96.5, 28.5)

# Search IMERG Final half-hourly
results = earthaccess.search_data(
    short_name="GPM_3IMERGHHL",
    version="07",
    temporal=date_range,
    bounding_box=bbox,
)

print(f"Granules found: {len(results)}")

# Optional filter (keep only useful files)
results = [r for r in results if "3B-HHR" in r.data_links()[0]]

# Output directory
outdir = r"F:\Saurabh\dashboard\GPM"
os.makedirs(outdir, exist_ok=True)

# Download (parallel)
files = earthaccess.download(results, local_path=outdir, threads=8)

print("Saved files:", len(files))