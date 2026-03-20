import matplotlib.pyplot as plt
import numpy as np

CMAP = plt.get_cmap("turbo")
def rain_to_rgba(rain):
    rain = np.clip(rain, 0, 50)

    norm = np.sqrt(rain / 50.0)

    r = np.zeros_like(norm)
    g = norm * 255
    b = (0.5 + 0.5 * norm) * 255
    a = np.where(rain > 0.2, norm * 220, 0)

    return np.stack([r, g, b, a], axis=0).astype("uint8")