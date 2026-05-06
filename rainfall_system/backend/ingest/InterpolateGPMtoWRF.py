import numpy as np
from scipy.interpolate import griddata

# Load WRF grid once
WRF_META_PATH = r"F:\Saurabh\dashboard\data\bin\meta.json"

import json
with open(WRF_META_PATH) as f:
    meta = json.load(f)

wrf_lat = np.array(meta["lat"])
wrf_lon = np.array(meta["lon"])

wrf_lon2d, wrf_lat2d = np.meshgrid(wrf_lon, wrf_lat)


def gpm_on_wrf(gpm_data, gpm_lat, gpm_lon):
    """Regrid GPM → WRF GRID """

    # create GPM grid
    gpm_lon2d, gpm_lat2d = np.meshgrid(gpm_lon, gpm_lat)

    # flatten
    points = np.column_stack((gpm_lon2d.ravel(), gpm_lat2d.ravel()))
    values = gpm_data.ravel()

    # interpolate
    result = griddata(
        points,
        values,
        (wrf_lon2d, wrf_lat2d),
        method="linear",
        fill_value=0
    )
    
    print("WRF grid:", wrf_lat2d.shape)
    

    return result.astype(np.float32)