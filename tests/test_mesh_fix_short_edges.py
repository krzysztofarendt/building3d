import numpy as np

from building3d import random_id
from building3d.config import GEOM_EPSILON
from building3d.geom.point import Point
from building3d.geom.vector import normal
from building3d.geom.wall import Wall
from building3d.mesh.mesh import Mesh


def test_fix_short_edges():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(0.1, 0.0, 0.0)
    p2 = Point(0.0, 10.0, 0.0)

    poly = Wall(random_id(), [p0, p1, p2])

    mesh = Mesh()
    mesh.add_polygon(poly)
    mesh.generate()
    mesh.collapse_points()

    # import pdb; pdb.set_trace()



if __name__ == "__main__":
    test_fix_short_edges()
