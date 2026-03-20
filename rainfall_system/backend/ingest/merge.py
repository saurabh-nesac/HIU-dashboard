from matplotlib.animation import FuncAnimation
import xarray as xr
import matplotlib.pyplot as plt

ds1 = xr.open_dataset(r"testfrema\FREMAA_2024060500Z.nc", 
                      engine="netcdf4")
ds2 = xr.open_dataset(r"testfrema\FREMAA_2024060600Z.nc", 
                      engine="netcdf4")

data = xr.merge([ds1,ds2], join="outer", compat="override")

rain = data['rain']
# rain_t0 = rain.isel(time=)
ds1 = ds1.expand_dims(run=["run1"])
ds2 = ds2.expand_dims(run=["run2"])

data = xr.concat([ds1, ds2], dim="run")


fig, ax = plt.subplots()

vmin = float(rain.min())
vmax = float(rain.max())

img = ax.imshow(
    rain.isel(time=0),
    cmap="turbo",
    origin="lower",   # 🔥 important
    extent=[
        float(rain.lon.min()),
        float(rain.lon.max()),
        float(rain.lat.min()),
        float(rain.lat.max())
    ]
)


def update(frame):
    img.set_array(rain.isel(time=frame))
    ax.set_title(f"Time: {str(rain.time.values[frame])}")
    return [img]
ani = FuncAnimation(fig, update, frames=len(rain.time), interval=100)

plt.show()

print(f'---------data----------',
      data)
print(f'---------ds1----------',
      ds1)

print(f'---------ds2----------',
      ds2)

print(data["rain"].values)
print(ds1["rain"].values)