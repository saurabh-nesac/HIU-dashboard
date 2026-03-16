import xarray as xr

def compute_rain_step(file):

    ds = xr.open_dataset(file)

    rain = ds["RAINC"] + ds["RAINNC"]

    rain_step = rain.diff("Time")

    return rain_step