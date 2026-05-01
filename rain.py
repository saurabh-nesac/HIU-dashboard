import numpy as np
import xarray as xr

# Load WRF output
ds = xr.open_dataset(r"rainfall_system\data\wrf_raw\wrfout_d02_2025-10-15_00_00_00")

# Extract staggered U and V
U = ds['U']   # (Time, bottom_top, south_north, west_east_stag)
V = ds['V']   # (Time, bottom_top, south_north_stag, west_east)

# --- Interpolate staggered grids to mass grid ---
U_mass = 0.5 * (U[:, :, :, :-1] + U[:, :, :, 1:])
V_mass = 0.5 * (V[:, :, :-1, :] + V[:, :, 1:, :])

# --- Compute wind speed and direction for all timesteps/levels ---
wind_speed = np.sqrt(U_mass**2 + V_mass**2)

wind_dir = np.degrees(np.arctan2(-U_mass, -V_mass))
wind_dir = (wind_dir + 360) % 360  # normalize to [0, 360)

# --- Wrap results into a new Dataset ---s
wind_ds = xr.Dataset(
    {
        "wind_speed": (["Time", "bottom_top", "south_north", "west_east"], wind_speed),
        "wind_dir":   (["Time", "bottom_top", "south_north", "west_east"], wind_dir),
    },
    coords={
        "Time": ds["Time"],
        "bottom_top": ds["bottom_top"],
        "south_north": ds["south_north"],
        "west_east": ds["west_east"],
    }
)

# Save to NetCDF for batch use
wind_ds.to_netcdf("wrf_wind_speed_direction.nc")
