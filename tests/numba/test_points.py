import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.points import are_points_collinear
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.points import point_to_str
from building3d.geom.numba.points import roll_forward
from building3d.geom.numba.types import FLOAT


def test_new_point():
    pt = new_point(0.0, 0.0, 0.0)
    assert isinstance(pt, np.ndarray)
    assert type(pt[0]) is FLOAT


def test_are_points_collinear():
    p1 = new_point(0.0, 0.0, 0.0)
    p2 = new_point(1.0, 0.0, 0.0)
    p3 = new_point(2.0, 0.0, 0.0)
    assert are_points_collinear(np.vstack([p1, p2, p3])) is True
    p3 = new_point(2.0, 1.0, 0.0)
    assert are_points_collinear(np.vstack([p1, p2, p3])) is False
    p3 = new_point(-2.0, 0.0, 0.0)
    assert are_points_collinear(np.vstack([p1, p2, p3])) is True


def test_are_points_coplanar():
    p1 = new_point(0.0, 0.0, 0.0)
    p2 = new_point(1.0, 0.5, 0.0)
    p3 = new_point(2.0, 0.0, 0.0)
    p4 = new_point(1.0, 1.0, 0.0)
    assert are_points_coplanar(np.vstack([p1, p2, p3, p4])) is True
    p4 = new_point(1.0, 1.0, 1.0)
    assert are_points_coplanar(np.vstack([p1, p2, p3, p4])) is False

    assert are_points_coplanar(np.vstack([p1, p2, p3])) is True
    assert are_points_coplanar(np.vstack([p1, p2])) is True
    assert are_points_coplanar(np.vstack([p1])) is True


def test_point_to_str():
    p = new_point(0.0, 0.0, 0.0)
    s = point_to_str(p)
    assert isinstance(s, str)
    assert "x=0.00" in s and "y=0.00" in s and "z=0.00" in s and "id=" in s


def test_roll_forward():
    p0 = new_point(0.0, 0.0, 0.0)
    p1 = new_point(1.0, 0.0, 0.0)
    p2 = new_point(2.0, 0.0, 0.0)
    pts = np.vstack((p0, p1, p2))
    assert np.allclose(pts[0], p0)
    assert np.allclose(pts[1], p1)
    assert np.allclose(pts[2], p2)
    pts = roll_forward(pts)
    assert np.allclose(pts[0], p2)
    assert np.allclose(pts[1], p0)
    assert np.allclose(pts[2], p1)
