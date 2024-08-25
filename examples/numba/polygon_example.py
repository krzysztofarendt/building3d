import numpy as np

from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.polygon import Polygon


if __name__ == "__main__":
    pts = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [2.0, 1.0, 0.0],
            [2.0, 2.0, 0.0],
            [1.0, 2.0, 0.0],
            [1.0, 3.0, 0.0],
            [0.0, 3.0, 0.0],
        ]
    )
    poly = Polygon(pts, name="poly0")

    plot_objects((poly,))
