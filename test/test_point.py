import numpy as np

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
