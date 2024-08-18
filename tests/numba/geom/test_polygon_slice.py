import numpy as np

from building3d.geom.numba.points import new_point, points_equal
from building3d.geom.numba.vectors import normal
from building3d.geom.numba.triangles import triangulate
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.slice import slice_polygon
from building3d.geom.numba.polygon.slice.locate_slicing_points import locate_slicing_points
from building3d.geom.numba.polygon.slice.remove_redundant_points import remove_redundant_points
from building3d.geom.numba.polygon.slice.constants import INTERIOR, VERTEX, EDGE


def test_slicing_point_location():
    pts = np.vstack((
        new_point(0, 0, 0),
        new_point(1, 0, 0),
        new_point(1, 1, 0),
        new_point(0, 1, 0),
    ))
    vn = normal(pts[-1], pts[0], pts[1])
    tri = triangulate(pts, vn)
    edges = polygon_edges(pts)

    # Check different slices
    slicing_pts = np.vstack((
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    loc = locate_slicing_points(slicing_pts, pts, tri, edges)
    assert loc[0] == (EDGE, 0)
    assert loc[1] == (EDGE, 2)

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    loc = locate_slicing_points(slicing_pts, pts, tri, edges)
    assert loc[0] == (VERTEX, 0)
    assert loc[1] == (EDGE, 0)
    assert loc[2] == (EDGE, 2)

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 0.5, 0),
        new_point(0.5, 1, 0),
        new_point(1, 0, 0),
    ))
    loc = locate_slicing_points(slicing_pts, pts, tri, edges)
    assert loc[0] == (VERTEX, 0)
    assert loc[1] == (EDGE, 0)
    assert loc[2] == (INTERIOR, -1)
    assert loc[3] == (EDGE, 2)
    assert loc[4] == (VERTEX, 1)


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
    vn = normal(pts[-1], pts[0], pts[1])
    tri = triangulate(pts, vn)
    edges = polygon_edges(pts)

    # Check different slices
    slicing_pts = np.vstack((
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    kept = remove_redundant_points(slicing_pts, pts, tri, edges)
    assert kept.shape == (2, 3)

    assert is_point_in(kept[0], slicing_pts)
    assert is_point_in(kept[1], slicing_pts)

    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    kept = remove_redundant_points(slicing_pts, pts, tri, edges)
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
    kept = remove_redundant_points(slicing_pts, pts, tri, edges)
    assert kept.shape == (3, 3)
    assert is_point_in(kept[0], slicing_pts[1:4])
    assert is_point_in(kept[1], slicing_pts[1:4])
    assert is_point_in(kept[2], slicing_pts[1:4])

    slicing_pts = np.vstack((
        new_point(-1, -1, -1),  # Point outside polygon
        new_point(0, 0, 0),
        new_point(0.5, 0, 0),
        new_point(0.5, 0.5, 0),
        new_point(0.5, 1, 0),
        new_point(1, 0, 0),
        new_point(3, 3, 3),  # Point outside polygon
    ))
    kept = remove_redundant_points(slicing_pts, pts, tri, edges)
    assert kept.shape == (3, 3)
    assert is_point_in(kept[0], slicing_pts[2:5])
    assert is_point_in(kept[1], slicing_pts[2:5])
    assert is_point_in(kept[2], slicing_pts[2:5])


def test_slice_polygon():
    pts = np.vstack((
        new_point(0, 0, 0),
        new_point(1, 0, 0),
        new_point(1, 1, 0),
        new_point(0, 1, 0),
    ))
    poly = Polygon(pts, "main")

    # Check different slices
    # Start at edge, end at another edge
    slicing_pts = np.vstack((
        new_point(0.5, 0, 0),
        new_point(0.5, 1, 0),
    ))
    name1 = "left"
    pt1 = new_point(0.25, 0.5, 0)
    name2 = "right"
    pt2 = new_point(0.75, 0.5, 0)
    poly1, poly2 = slice_polygon(poly, slicing_pts, pt1, name1, pt2, name2)
    print(poly1, poly2)

    # Start and end at the same edge
    slicing_pts = np.vstack((
        new_point(0.6, 0, 0),
        new_point(0.6, 0.5, 0),
        new_point(0.4, 0.5, 0),
        new_point(0.4, 0.0, 0),
    ))
    name1 = "left"
    pt1 = new_point(0.25, 0.5, 0)
    name2 = "right"
    pt2 = new_point(0.5, 0.25, 0)
    poly1, poly2 = slice_polygon(poly, slicing_pts, pt1, name1, pt2, name2)
    print(poly1, poly2)

    # Start at vertex, end at edge
    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(0.5, 0.5, 0),
        new_point(0.5, 1, 0),
    ))
    name1 = "left"
    pt1 = new_point(0.25, 0.9, 0)
    name2 = "right"
    pt2 = new_point(0.75, 0.1, 0)
    poly1, poly2 = slice_polygon(poly, slicing_pts, pt1, name1, pt2, name2)
    print(poly1, poly2)

    # Start at vertex, end at different vertex
    slicing_pts = np.vstack((
        new_point(0, 0, 0),
        new_point(1, 1, 0),
    ))
    name1 = "left"
    pt1 = new_point(0.1, 0.9, 0)
    name2 = "right"
    pt2 = new_point(0.9, 0.1, 0)
    poly1, poly2 = slice_polygon(poly, slicing_pts, pt1, name1, pt2, name2)
    print(poly1, poly2)


# def test_polygon_slice_using_another_polygon():
#     pt0 = new_point(0, 0, 0)
#     pt1 = new_point(1, 0, 0)
#     pt2 = new_point(1, 1, 0)
#     pt3 = new_point(0, 1, 0)
#     pts = np.vstack((pt0, pt1, pt2, pt3))
#     poly1 = Polygon(pts, name="poly1")
#
#     dxy = np.array([0.5, 0.5, 0.0])
#     poly2 = Polygon(pts + dxy, name="poly2")
#
#     # TODO: Need to add slicing points at cross-section of lines
#     poly3, poly4 = slice_polygon(
#         poly1,
#         poly2.pts,
#         pt1=new_point(0.25, 0.25, 0),
#         name1="poly3",
#         pt2=new_point(0.75, 0.75, 0),
#         name2="poly4",
#     )
#     assert len(poly4.pts) == 4  # square
#     assert len(poly3.pts) == 6  # L-shape


if __name__ == "__main__":
    test_slice_polygon()