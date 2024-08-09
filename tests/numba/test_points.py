import numpy as np

from building3d.geom.numba.points import are_points_collinear
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.points import point_to_str


def test_are_points_collinear():
    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([1.0, 0.0, 0.0])
    p3 = np.array([2.0, 0.0, 0.0])
    assert are_points_collinear(np.vstack([p1, p2, p3])) is True
    p3 = np.array([2.0, 1.0, 0.0])
    assert are_points_collinear(np.vstack([p1, p2, p3])) is False
    p3 = np.array([-2.0, 0.0, 0.0])
    assert are_points_collinear(np.vstack([p1, p2, p3])) is True


def test_are_points_coplanar():
    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([1.0, 0.5, 0.0])
    p3 = np.array([2.0, 0.0, 0.0])
    p4 = np.array([1.0, 1.0, 0.0])
    assert are_points_coplanar(np.vstack([p1, p2, p3, p4])) is True
    p4 = np.array([1.0, 1.0, 1.0])
    assert are_points_coplanar(np.vstack([p1, p2, p3, p4])) is False

    assert are_points_coplanar(np.vstack([p1, p2, p3])) is True
    assert are_points_coplanar(np.vstack([p1, p2])) is True
    assert are_points_coplanar(np.vstack([p1])) is True


def test_point_to_str():
    p = np.array([0.0, 0.0, 0.0])
    s = point_to_str(p)
    assert isinstance(s, str)
    assert "x=0.00" in s and "y=0.00" in s and "z=0.00" in s and "id=" in s

