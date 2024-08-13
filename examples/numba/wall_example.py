import numpy as np

from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall


if __name__ == "__main__":
    pts = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [2.0, 1.0, 0.0],
        [2.0, 2.0, 0.0],
        [1.0, 2.0, 0.0],
        [1.0, 3.0, 0.0],
        [0.0, 3.0, 0.0],
    ])
    poly = Polygon(pts, name="poly0")
    wall = Wall([poly], name="wall0")

    plot_objects((wall, ))
