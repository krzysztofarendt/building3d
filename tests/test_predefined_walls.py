import numpy as np

from building3d.geom.predefined.walls import vertical_wall
from building3d.geom.predefined.walls import vertical_wall_with_aperture


def test_wall_orientation():
    w = vertical_wall(
        width=2.0,
        height=1.0,
        translate=(0.0, 0.0, 0.0),
        rot_angle=0.0,
    )

    poly = w.get_polygons()[0]
    assert np.isclose(
        poly.normal, np.array([0, 1, 0])
    ).all(), "Wall normal should be (0, 1, 0) according to the documentation of vertical_wall()"


def test_wall_orientation_rot90_degrees():
    w = vertical_wall(
        width=2.0,
        height=1.0,
        translate=(0.0, 0.0, 0.0),
        rot_angle=np.pi / 2.0,
    )

    poly = w.get_polygons()[0]
    assert np.isclose(poly.normal, np.array([-1, 0, 0])).all()


def test_wall_with_aperture_orientation():
    w = vertical_wall_with_aperture(
        width=2.0,
        height=1.0,
        translate=(0.0, 0.0, 0.0),
        rot_angle=0.0,
        aperture_width=1.0,
        aperture_height=0.5,
        aperture_xz_offset=(0.5, 0.25),
    )

    polys = w.get_polygons(only_parents=False)
    for p in polys:
        assert np.isclose(p.normal, np.array([0, 1, 0])).all(), (
            "Wall normal should be (0, 1, 0) according to the documentation of "
            "vertical_wall_with_aperture()"
        )
