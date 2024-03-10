import numpy as np

from building3d.geom.vector import angle


def test_angle():
    eps = 1e-8

    # Angle 90 degrees
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    assert np.abs(angle(v1, v2) - np.pi / 2) < eps

    # Angle 0 degrees
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    assert angle(v1, v2) < eps
