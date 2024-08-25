import numpy as np


def random_rgb_color() -> list[float]:
    """Return a random RGB color for the PyVista plotter."""
    return np.random.random(3).tolist()
