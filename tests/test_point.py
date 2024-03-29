import numpy as np
import pytest

from building3d.geom.point import Point


def test_add_vector_to_a_point():
    vector = [1.0, 1.0, 1.0]
    p1 = Point(0.0, 0.0, 0.0)
    p2 = p1 + vector
    assert np.isclose(p2.x, 1.0) and np.isclose(p2.y, 1.0) and np.isclose(p2.z, 1.0)

    vector = np.array([-1.0, -1.0, -1.0])
    p1 = Point(0.0, 0.0, 0.0)
    p2 = p1 + vector
    assert np.isclose(p2.x, -1.0) and np.isclose(p2.y, -1.0) and np.isclose(p2.z, -1.0)

    p0 = Point(2.0, 2.0, 2.0)
    p1 = Point(0.0, 0.0, 0.0)
    p2 = p1 + p0.vector()
    assert np.isclose(p2.x, p0.x) and np.isclose(p2.y, p0.y) and np.isclose(p2.z, p0.z)


def test_radd_vector_to_a_point():
    vector = [1.0, 1.0, 1.0]
    p1 = Point(0.0, 0.0, 0.0)
    p2 = vector + p1
    assert np.isclose(p2.x, 1.0) and np.isclose(p2.y, 1.0) and np.isclose(p2.z, 1.0)

    vector = np.array([-1.0, -1.0, -1.0])
    p1 = Point(0.0, 0.0, 0.0)
    with pytest.raises(TypeError):
        # This is not allowed, because of numpy's broadcasting
        p2 = vector + p1

    p0 = Point(2.0, 2.0, 2.0)
    p1 = Point(0.0, 0.0, 0.0)
    with pytest.raises(TypeError):
        # This is not allowed, because of numpy's broadcasting
        p2 = p0.vector() + p1


def test_mul_vector_with_a_point():
    vector = [2.0, 2.0, 2.0]
    p1 = Point(2.0, 3.0, 4.0)
    p2 = p1 * vector
    assert np.isclose(p2.x, 4.0) and np.isclose(p2.y, 6.0) and np.isclose(p2.z, 8.0)

    vector = np.array([2.0, 2.0, 2.0])
    p1 = Point(2.0, 3.0, 4.0)
    p2 = p1 * vector
    assert np.isclose(p2.x, 4.0) and np.isclose(p2.y, 6.0) and np.isclose(p2.z, 8.0)

    p0 = Point(2.0, 2.0, 2.0)
    p1 = Point(2.0, 3.0, 4.0)
    p2 = p1 * p0.vector()
    assert np.isclose(p2.x, 4.0) and np.isclose(p2.y, 6.0) and np.isclose(p2.z, 8.0)


def test_rmul_vector_with_a_point():
    vector = [2.0, 2.0, 2.0]
    p1 = Point(2.0, 3.0, 4.0)
    p2 = vector * p1
    assert np.isclose(p2.x, 4.0) and np.isclose(p2.y, 6.0) and np.isclose(p2.z, 8.0)

    vector = np.array([2.0, 2.0, 2.0])
    p1 = Point(2.0, 3.0, 4.0)
    with pytest.raises(TypeError):
        # This is not allowed, because of numpy's broadcasting
        p2 = vector * p1

    p0 = Point(2.0, 2.0, 2.0)
    p1 = Point(2.0, 3.0, 4.0)
    with pytest.raises(TypeError):
        # This is not allowed, because of numpy's broadcasting
        p2 = p0.vector() * p1


def test_copy():
    p1 = Point(2.0, 3.0, 4.0)
    p2 = p1.copy()
    assert p1 == p2
    assert not (p1 is p2)
