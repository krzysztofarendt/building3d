import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon.slice import slicing_point_location


def test_slicing_point_location():
    pts = np.vstack((
        new_point(0, 0, 0),
        new_point(1, 0, 0),
        new_point(1, 1, 0),
        new_point(0, 1, 0),
    ))
    # Check different slices
    slicing_pts = np.vstack((
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    loc = slicing_point_location(pts, slicing_pts)
    assert loc[0] == ("at_edge", 0)
    assert loc[1] == ("at_edge", 2)

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    loc = slicing_point_location(pts, slicing_pts)
    assert loc[0] == ("at_vertex", 0)
    assert loc[1] == ("at_edge", 0)
    assert loc[2] == ("at_edge", 2)

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 0.5, 0),
        new_point(0.5, 1, 0),
        new_point(1, 0, 0),
    ))
    loc = slicing_point_location(pts, slicing_pts)
    assert loc[0] == ("at_vertex", 0)
    assert loc[1] == ("at_edge", 0)
    assert loc[2] == ("interior", -1)
    assert loc[3] == ("at_edge", 2)
    assert loc[4] == ("at_vertex", 1)


if __name__ == "__main__":
    test_slicing_point_location()
