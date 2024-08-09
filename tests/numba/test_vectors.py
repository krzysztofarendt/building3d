import numpy as np
import pytest

from building3d.geom.numba.vectors import normal


def test_normal():
    pt0 = np.array([0.0, 0.0, 0.0])
    pt1 = np.array([1.0, 0.0, 0.0])
    pt2 = np.array([1.0, 1.0, 0.0])

    n = normal(pt0, pt1, pt2)
    assert np.allclose(n, [0, 0, 1])

    pt0 = np.array([0.0, 0.0, 0.0])
    pt1 = np.array([1.0, 0.0, 0.0])
    pt2 = np.array([2.0, 0.0, 0.0])

    n = normal(pt0, pt1, pt2)
    assert np.isnan(n).all()
