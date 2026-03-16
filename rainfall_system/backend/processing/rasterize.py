import rasterio

def write_tif(rgba, transform, path):

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=rgba.shape[0],
        width=rgba.shape[1],
        count=4,
        dtype="uint8",
        crs="EPSG:3857",
        transform=transform
    ) as dst:

        for i in range(4):
            dst.write(rgba[:,:,i], i+1)