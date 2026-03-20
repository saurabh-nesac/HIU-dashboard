import xarray as xr

def compute_rain_step(rain_all, t):
    frame = rain_all[t] - rain_all[t-1]
    frame[frame < 0] = 0
    return frame