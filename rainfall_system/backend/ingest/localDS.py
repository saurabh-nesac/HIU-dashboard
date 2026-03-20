import xarray as xr
import dask


dsLocal = xr.open_dataset(r"wrfFrema\3km\FREMAA_2024060500Z.nc", engine="netcdf4")

# ds = xr.open_mfdataset(r"wrfFrema\3km\*.nc",concat_dim=[],combine="by_coords", parallel=True ,engine="netcdf4")

print(dsLocal)
print("Variables:")
print(list(dsLocal.variables))
print(dsLocal.rain)
# print(dsLocal['time'].values)

# print(ds)
# print("Variables:")
# print(list(ds.variables))
# print(ds['time'].values)

# time_index = ds.get_index('time')
# duplicate_mask = time_index.duplicated(keep=False)

# print(time_index[duplicate_mask], sep=',')