import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.tetrahedrons import tetrahedron_centroid
from building3d.geom.numba.tetrahedrons import tetrahedron_volume


def test_tetrahedron_centroid():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(0, 1, 0)
    pt3 = new_point(0, 0, 1)
    ctr = tetrahedron_centroid(pt0, pt1, pt2, pt3)
    assert np.allclose(ctr, [1/4, 1/4, 1/4])


def test_tetrahedron_volume():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(0, 1, 0)
    pt3 = new_point(0, 0, 1)
    vol = tetrahedron_volume(pt0, pt1, pt2, pt3)
    # Below volume calculated using: http://tamivox.org/redbear/tetra_calc/index.html
    assert np.isclose(vol, 0.1666666667)
