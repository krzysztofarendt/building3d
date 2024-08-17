import numpy as np

from building3d.geom.numba.points import new_point, points_equal
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.slice import slicing_point_location
from building3d.geom.numba.polygon.slice import remove_redundant_points


def test_slicing_point_location():
    pts = np.vstack((
        new_point(0, 0, 0),
        new_point(1, 0, 0),
        new_point(1, 1, 0),
        new_point(0, 1, 0),
    ))
    poly_edges = polygon_edges(pts)

    # Check different slices
    slicing_pts = np.vstack((
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    loc = slicing_point_location(pts, slicing_pts, poly_edges)
    assert loc[0] == ("at_edge", 0)
    assert loc[1] == ("at_edge", 2)

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    loc = slicing_point_location(pts, slicing_pts, poly_edges)
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
    loc = slicing_point_location(pts, slicing_pts, poly_edges)
    assert loc[0] == ("at_vertex", 0)
    assert loc[1] == ("at_edge", 0)
    assert loc[2] == ("interior", -1)
    assert loc[3] == ("at_edge", 2)
    assert loc[4] == ("at_vertex", 1)


def test_remove_redundant_points():

    def is_point_in(pt, arr):
        for i in range(arr.shape[0]):
            if points_equal(arr[i], pt):
                return True
        return False

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
    kept = remove_redundant_points(pts, slicing_pts)
    assert kept.shape == (2, 3)

    assert is_point_in(kept[0], slicing_pts)
    assert is_point_in(kept[1], slicing_pts)

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    kept = remove_redundant_points(pts, slicing_pts)
    assert kept.shape == (2, 3)
    assert is_point_in(kept[0], slicing_pts[1:])
    assert is_point_in(kept[1], slicing_pts[1:])

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 0.5, 0),
        new_point(0.5, 1, 0),
        new_point(1, 0, 0),
    ))
    kept = remove_redundant_points(pts, slicing_pts)
    assert kept.shape == (3, 3)
    assert is_point_in(kept[0], slicing_pts[1:4])
    assert is_point_in(kept[1], slicing_pts[1:4])
    assert is_point_in(kept[2], slicing_pts[1:4])


if __name__ == "__main__":
    test_remove_redundant_points()
