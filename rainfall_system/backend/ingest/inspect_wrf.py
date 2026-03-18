import xarray as xr

WRF_FILE = r"rainfall_system\data\wrf_raw\wrfout_d02_2025-10-15_00_00_00"

ds = xr.open_dataset(WRF_FILE)

print(ds)
print("Variables:")
print(list(ds.variables))