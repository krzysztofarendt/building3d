import numpy as np

from building3d.geom.points import new_point
from building3d.geom.vectors import normal
from building3d.geom.triangles import triangulate
from building3d.geom.polygon.crossing import are_polygons_crossing


def test_orthogonal_rectangles():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(1.0, 2.0, 0.0)
    pt4 = new_point(0.0, 2.0, 0.0)
    pts1 = np.array([pt1, pt2, pt3, pt4])
    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    pts1, tri1 = triangulate(pts1, vn1)

    pt1 = new_point(0.0, 1.0, 0.0)
    pt2 = new_point(2.0, 1.0, 0.0)
    pt3 = new_point(2.0, 2.0, 0.0)
    pt4 = new_point(0.0, 2.0, 0.0)
    pts2 = np.array([pt1, pt2, pt3, pt4])
    vn2 = normal(pts2[-1], pts2[0], pts2[1])
    pts2, tri2 = triangulate(pts2, vn2)

    assert are_polygons_crossing(pts1, tri1, pts2, tri2) is True


def test_adjacent_rectangles():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(1.0, 1.0, 0.0)
    pt4 = new_point(0.0, 1.0, 0.0)
    pts1 = np.array([pt1, pt2, pt3, pt4])
    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    pts1, tri1 = triangulate(pts1, vn1)

    pts2 = pts1 + np.array([1.0, 0.0, 0.0])
    vn2 = normal(pts2[-1], pts2[0], pts2[1])
    pts2, tri2 = triangulate(pts2, vn2)

    assert are_polygons_crossing(pts1, tri1, pts2, tri2) is False


def test_overlapping_rectangles():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(1.0, 1.0, 0.0)
    pt4 = new_point(0.0, 1.0, 0.0)
    pts1 = np.array([pt1, pt2, pt3, pt4])
    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    pts1, tri1 = triangulate(pts1, vn1)

    pts2 = pts1 + np.array([0.5, 0.0, 0.0])
    vn2 = normal(pts2[-1], pts2[0], pts2[1])
    pts2, tri2 = triangulate(pts2, vn2)

    assert are_polygons_crossing(pts1, tri1, pts2, tri2) is True


def test_rectangles_diff_z():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(1.0, 2.0, 0.0)
    pt4 = new_point(0.0, 2.0, 0.0)
    pts1 = np.array([pt1, pt2, pt3, pt4])
    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    pts1, tri1 = triangulate(pts1, vn1)

    pt1 = new_point(0.0, 1.0, 1.0)
    pt2 = new_point(2.0, 1.0, 1.0)
    pt3 = new_point(2.0, 2.0, 1.0)
    pt4 = new_point(0.0, 2.0, 1.0)
    pts2 = np.array([pt1, pt2, pt3, pt4])
    vn2 = normal(pts2[-1], pts2[0], pts2[1])
    pts2, tri2 = triangulate(pts2, vn2)

    assert are_polygons_crossing(pts1, tri1, pts2, tri2) is False


def test_same_rectangles():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(1.0, 2.0, 0.0)
    pt4 = new_point(0.0, 2.0, 0.0)
    pts1 = np.array([pt1, pt2, pt3, pt4])
    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    pts1, tri1 = triangulate(pts1, vn1)

    assert are_polygons_crossing(pts1, tri1, pts1.copy(), tri1.copy()) is False
