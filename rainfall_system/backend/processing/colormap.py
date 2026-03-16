import matplotlib.pyplot as plt
import numpy as np

CMAP = plt.get_cmap("turbo")

def rain_to_rgba(rain):

    norm = np.clip(rain / 50.0, 0, 1)

    rgba = CMAP(norm)

    rgba[...,3] = np.where(rain > 0.1, 0.8, 0)

    return (rgba * 255).astype(np.uint8)