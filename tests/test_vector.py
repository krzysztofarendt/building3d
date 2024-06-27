import numpy as np

from building3d.geom.point import Point
from building3d.geom.vector import angle
from building3d.geom.vector import angle_ccw
from building3d.geom.vector import are_vectors_colinear


def test_angle():
    eps = 1e-8

    # Angle 90 degrees
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    assert np.abs(angle(v1, v2) - np.pi / 2) < eps

    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 0.0, 1.0])
    assert np.abs(angle(v1, v2) - np.pi / 2) < eps

    # Angle 45 degrees
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 1.0, 0.0])
    assert np.abs(angle(v1, v2) - np.pi / 4) < eps

    # Angle 0 degrees
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    assert angle(v1, v2) < eps

    v1 = np.array([0.0, 0.0, 1.0])
    v2 = np.array([0.0, 0.0, 1.0])
    assert angle(v1, v2) < eps

    # Test angle == 180 degrees
    v1 = np.array([-1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    assert np.abs(angle(v1, v2) - np.pi) < eps

    # Test angles > 180 degrees
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([-1.0, -0.5, 0.0])
    assert angle(v1, v2) < np.pi
    assert angle_ccw(v1, v2, np.cross(v2, v1)) > np.pi
    assert angle_ccw(v2, v1, np.cross(v1, v2)) > np.pi


def test_are_vectors_colinear():
    v1 = (Point(0, 0, 0), Point(1, 0, 0))
    v2 = (Point(0.5, 0, 0), Point(10, 0, 0))
    assert are_vectors_colinear(v1, v2)

    v3 = (Point(0.5, 0, 0.01), Point(10, 0, 0))
    assert not are_vectors_colinear(v1, v3)
