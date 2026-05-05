import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import geopandas as gpd

# --- LOAD DATA ---
ds = xr.open_dataset(r'F:\Saurabh\dashboard\wrfFrema\3km\FREMAA_2024060500Z.nc')

rain_inst = ds['rain'].diff(dim='time')
lat = ds['lat']
lon = ds['lon']
time_in = ds['time'].values
print(time_in)

# --- LOAD SHAPEFILE ---
shp_path = r'rainfall_system\data\shapefile\ne_states.geojson'  # <-- your shapefile
gdf = gpd.read_file(shp_path)

# Ensure CRS is WGS84 (lat/lon)
gdf = gdf.to_crs(epsg=4326)

# --- SETTINGS ---
t0 = 0
vmin0 = 0
vmax0 = float(rain_inst.max())
threshold = 1

# --- COLORMAP ---
cmap = plt.cm.get_cmap('jet').copy()
cmap.set_bad(color='none')

# --- INITIAL DATA ---
data = rain_inst.isel(time=t0).values
data = np.ma.masked_invalid(data)
data = np.ma.masked_less(data, threshold)

# --- PLOT ---
fig, ax = plt.subplots(figsize=(10,8))
plt.subplots_adjust(bottom=0.28)

mesh = ax.pcolormesh(
    lon,
    lat,
    data,
    cmap=cmap,
    shading='auto',
    vmin=vmin0,
    vmax=vmax0
)

plt.colorbar(mesh, ax=ax, label="Rainfall (mm)")

# --- ADD SHAPEFILE OVERLAY ---
gdf.boundary.plot(ax=ax, color='black', linewidth=0.8)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

time_val = ds['time'].isel(time=t0).values
ax.set_title(f"Time: {time_val}")

# --- SLIDERS ---

# Time slider
ax_time = plt.axes([0.2, 0.15, 0.6, 0.03])
slider_time = Slider(ax_time, 'Time', 0, time_in , valinit=t0, valstep=1)

# Min slider
ax_min = plt.axes([0.2, 0.09, 0.25, 0.03])
slider_min = Slider(ax_min, 'Min', 0, vmax0, valinit=vmin0)

# Max slider
ax_max = plt.axes([0.55, 0.09, 0.25, 0.03])
slider_max = Slider(ax_max, 'Max', 0, vmax0, valinit=vmax0)

# --- UPDATE FUNCTION ---
def update(val):
    t = int(slider_time.val)
    vmin = slider_min.val
    vmax = slider_max.val

    if vmin >= vmax:
        return

    new_data = rain_inst.isel(time=t).values
    new_data = np.ma.masked_invalid(new_data)
    new_data = np.ma.masked_less(new_data, threshold)

    mesh.set_array(new_data.ravel())
    mesh.set_clim(vmin, vmax)

    time_val = ds['time'].isel(time=t).values
    ax.set_title(f"Time: {time_val} | Range: {vmin:.2f}-{vmax:.2f} mm")

    fig.canvas.draw_idle()

slider_time.on_changed(update)
slider_min.on_changed(update)
slider_max.on_changed(update)

plt.show()