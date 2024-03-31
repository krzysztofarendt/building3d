import numpy as np

from building3d.geom.point import Point
from building3d.geom.rotate import rotate_points_around_vector
from building3d.geom.rotate import rotate_points_to_plane
from building3d.geom.vector import normal


def test_rotate_points_around_vector():
    p0 = Point(1.0, 0.0, 0.0)
    p1 = Point(0.0, 1.0, 0.0)
    p2 = Point(0.0, 0.0, 0.0)

    rotated_points, _ = rotate_points_around_vector(
        points=[p0, p1, p2],
        u=np.array([0.0, 1.0, 0.0]),
        phi=-np.pi / 2,
    )

    assert rotated_points[0] == Point(0.0, 0.0, 1.0)
    assert rotated_points[1] == Point(0.0, 1.0, 0.0)
    assert rotated_points[2] == Point(0.0, 0.0, 0.0)


def test_rotate_points_to_plane_anchor_nonzero():
    p0 = Point(1.0, 0.0, 0.0)
    p1 = Point(0.0, 1.0, 0.0)
    p2 = Point(0.0, 0.0, 0.0)
    normal_target = np.array([1.0, 0.0, 0.0])
    target_plane_d = 1.0

    rotated_points, _, _ = rotate_points_to_plane(
        points=[p0, p1, p2],
        anchor=p0,
        u=normal_target,
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


def test_rotate_points_to_plane_anchor_origin():
    p0 = Point(1.0, 0.0, 0.0)
    p1 = Point(0.0, 1.0, 0.0)
    p2 = Point(0.0, 0.0, 0.0)
    origin = Point(0.0, 0.0, 0.0)
    normal_target = np.array([1.0, 0.0, 0.0])
    target_plane_d = 1.0

    rotated_points, _, _ = rotate_points_to_plane(
        points=[p0, p1, p2],
        anchor=origin,
        u=normal_target,
        d=target_plane_d,
    )

    # The triangle was rotated around origin (0.0, 0.0, 0.0)
    # around the Y axis so that the resulting normal
    # is [1.0, 0.0, 0.0]. In addition, the triangle
    # has been moved +1 in the X direction due to d=1.
    # So all points should have x=1.0.
    for i in range(3):
        assert np.isclose(rotated_points[i].x, 1.0)

    normal_res = normal(*rotated_points)
    assert np.isclose(normal_res, normal_target).all()


def test_rotate_points_to_plane_anchor_origin_d0():
    p0 = Point(1.0, 0.0, 0.0)
    p1 = Point(0.0, 1.0, 0.0)
    p2 = Point(0.0, 0.0, 0.0)
    origin = Point(0.0, 0.0, 0.0)
    normal_target = np.array([1.0, 0.0, 0.0])
    target_plane_d = 0.0

    rotated_points, _, _ = rotate_points_to_plane(
        points=[p0, p1, p2],
        anchor=origin,
        u=normal_target,
        d=target_plane_d,
    )

    # The triangle was rotated around p0 (1.0, 0.0, 0.0)
    # around the Y axis so that the resulting normal
    # is [1.0, 0.0, 0.0]. In addition, d=0, so
    # so all points should have x=0.
    for i in range(3):
        assert np.isclose(rotated_points[i].x, 0.0)

    normal_res = normal(*rotated_points)
    assert np.isclose(normal_res, normal_target).all()


def test_rotate_back():
    p0 = Point(1.0, 0.0, 1.0)
    p1 = Point(0.0, 1.0, 1.0)
    p2 = Point(0.0, 0.0, 1.0)

    original_points = [p0, p1, p2]
    origin = Point(0.0, 0.0, 0.0)

    normal_target = np.array([1.0, 0.0, 0.0])
    target_plane_d = 0.0

    rotated_points, rotaxis, phi = rotate_points_to_plane(
        points=[p0, p1, p2],
        anchor=origin,
        u=normal_target,
        d=target_plane_d,
    )
    # Inverse rotation
    # It works only if there is no translation involved (i.e. when achor=(0,0,0) and d=0)
    rotated_back_points, _ = rotate_points_around_vector(rotated_points, rotaxis, -phi)
    assert set(rotated_back_points) == set(original_points)


def test_slanted_roof():
    p0 = Point(0.0, 0.0, 1.0)
    p1 = Point(1.0, 0.0, 0.5)
    p2 = Point(1.0, 1.0, 1.0)
    p3 = Point(0.0, 1.0, 1.5)

    # Rotate to XY plane
    points = [p0, p1, p2, p3]
    rotated_points, rotaxis, phi = rotate_points_to_plane(
        points,
        anchor=Point(0.0, 0.0, 0.0),
        u=np.array([0.0, 0.0, 1.0]),
        d=0.0,
    )
    rot_p0, rot_p1, rot_p2, rot_p3 = rotated_points
    assert np.isclose(rot_p0.z, rot_p1.z)
    assert np.isclose(rot_p0.z, rot_p2.z)
    assert np.isclose(rot_p0.z, rot_p3.z)

    # Rotate back
    rerotated_points, _ = rotate_points_around_vector(rotated_points, rotaxis, -phi)
    rerot_p0, rerot_p1, rerot_p2, rerot_p3 = rerotated_points
    assert rerot_p0 == p0
    assert rerot_p1 == p1
    assert rerot_p2 == p2
    assert rerot_p3 == p3


def test_rotate_from_xy_to_xy():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)

    # Rotate to XY plane
    points = [p0, p1, p2, p3]

    rotated_points, rotaxis, phi = rotate_points_to_plane(
        points,
        anchor=Point(0.0, 0.0, 0.0),
        u=np.array([0.0, 0.0, 1.0]),
        d=0.0,
    )
    rot_p0, rot_p1, rot_p2, rot_p3 = rotated_points
    assert np.isclose(rot_p0.z, rot_p1.z)
    assert np.isclose(rot_p0.z, rot_p2.z)
    assert np.isclose(rot_p0.z, rot_p3.z)

    # Rotate back
    rerotated_points, _ = rotate_points_around_vector(rotated_points, rotaxis, -phi)
    rerot_p0, rerot_p1, rerot_p2, rerot_p3 = rerotated_points
    assert rerot_p0 == p0
    assert rerot_p1 == p1
    assert rerot_p2 == p2
    assert rerot_p3 == p3


if __name__ == "__main__":
    test_rotate_from_xy_to_xy()
