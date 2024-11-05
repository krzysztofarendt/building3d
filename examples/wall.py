import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall

if __name__ == "__main__":
    print("This example shows how to create a wall from a set of points.")

    pts0 = np.array(
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
    poly0 = Polygon(pts0, name="poly0")

    pts1 = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
        ]
    )
    poly1 = Polygon(pts1, name="poly1")

    wall = Wall([poly0, poly1], name="wall0")

    plot_objects((wall,))
