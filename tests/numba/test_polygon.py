import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon import polygon_centroid


def test_polygon_centroid_square():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    tri = np.array([
            [0, 1, 2],
            [2, 3, 0],
    ])
    ctr = polygon_centroid(pts, tri)
    assert np.allclose(ctr, [0.5, 0.5, 0.0])
