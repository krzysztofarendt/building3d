import numpy as np

from building3d.geom.point import Point
from building3d.geom.rotate import rotate_points_around_vector
from building3d.geom.rotate import rotate_points_to_plane
from building3d.geom.vector import normal


def test_rotate_points_around_vector():
    p0 = Point(1.0, 0.0, 0.0)
    p1 = Point(0.0, 1.0, 0.0)
    p2 = Point(0.0, 0.0, 0.0)

    rotated_points = rotate_points_around_vector(
        points=[p0, p1, p2],
        u=np.array([0.0, 1.0, 0.0]),
        phi=-np.pi/2,
    )

    assert rotated_points[0] == Point(0.0, 0.0, 1.0)
    assert rotated_points[1] == Point(0.0, 1.0, 0.0)
    assert rotated_points[2] == Point(0.0, 0.0, 0.0)


def test_rotate_points_to_plane():
    p0 = Point(1.0, 0.0, 0.0)
    p1 = Point(0.0, 1.0, 0.0)
    p2 = Point(0.0, 0.0, 0.0)
    # normal_orig = np.array([0.0, 0.0, 1.0])
    normal_target = np.array([1.0, 0.0, 0.0])
    target_plane_d = 1.0

    rotated_points = rotate_points_to_plane(
        points=[p0, p1, p2],
        anchor=p0,
        normal=normal_target,
        d=target_plane_d,
    )

    # The triangle was rotated around p0 (1.0, 0.0, 0.0)
    # around the Y axis so that the resulting normal
    # is [1.0, 0.0, 0.0]. In addition, the triangle
    # has been moved +1 in the X direction due to d=1.
    # So all points should have x=2.
    for i in range(3):
        assert np.isclose(rotated_points[i].x, 2.0)

    normal_res = normal(*rotated_points)
    assert np.isclose(normal_res, normal_target).all()
