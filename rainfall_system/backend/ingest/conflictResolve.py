import numpy as np
from matplotlib.animation import FuncAnimation
import xarray as xr

ds1 = xr.open_dataset(r"testfrema\FREMAA_2024060500Z.nc", 
                      engine="netcdf4")
ds2 = xr.open_dataset(r"testfrema\FREMAA_2024060600Z.nc", 
                      engine="netcdf4")

t1 = set(ds1["time"].values)
t2 = set(ds2["time"].values)

overlap = sorted(t1.intersection(t2))

print("Overlapping timestamps:",overlap)
print("Count:", len(overlap))


for t in overlap[:5]:   # check first few
    r1 = ds1.sel(time=t)["rain"]
    r2 = ds2.sel(time=t)["rain"]

    diff = r1 - r2

    max_diff = float(np.nanmax(np.abs(diff)))
    mean_diff = float(np.nanmean(np.abs(diff)))

    print(f"\nTime: {t}")
    print(f"Max diff: {max_diff}")
    print(f"Mean diff: {mean_diff}")
    
rain = data["rain"]

fig, ax = plt.subplots()

img = ax.imshow(rain.isel(run=0, time=0), cmap="turbo")

def update(frame):
    t = frame % len(rain.time)
    r = frame // len(rain.time)

    img.set_array(rain.isel(run=r, time=t))
    ax.set_title(f"Run={r}, Time={t}")
    return [img]

frames = len(rain.time) * len(rain.run)

ani = FuncAnimation(fig, update, frames=frames)
plt.show()