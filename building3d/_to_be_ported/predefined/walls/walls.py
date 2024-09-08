"""Predefined walls.

The walls are vertical by default and located on the XZ plane.
Their orientation can be changed using the `rot_vec` and `rot_angle` parameters.
Their location can be changed using the `translate` parameter.
"""

import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.rotate import rotate_points_around_vector


def vertical_wall(
    width: float,
    height: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_vec: tuple[float, float, float] = (0.0, 0.0, 1.0),
    rot_angle: float = 0.0,
    name: str | None = None,
) -> Wall:
    """Create a Wall with given dimensions, located at `translate`.

    By default, the wall is vertical and located on the XZ plane
    with the normal pointing towards (0, 1, 0).

    Order of transformations:
    - create a wall with the first vertex at (0, 0, 0)
    - apply rotation
    - apply translation

    Args:
        width: Width of the wall
        height: Height of the wall
        translate: Origin of the wall
        rot_vec: Vector describing the rotation of the wall
        rot_angle: Angle of the rotation (in radians)
        name: Name of the wall (random if None)

    Return:
        Wall
    """
    vec = np.array(rot_vec)

    p0 = Point(0, 0, 0)
    p1 = Point(0, 0, height)
    p2 = Point(width, 0, height)
    p3 = Point(width, 0, 0)

    if rot_angle != 0:
        (p0, p1, p2, p3), _ = rotate_points_around_vector(
            points=[p0, p1, p2, p3],
            u=vec,
            phi=rot_angle,
        )

    p0 += translate
    p1 += translate
    p2 += translate
    p3 += translate

    poly = Polygon([p0, p1, p2, p3], name=name)
    wall = Wall([poly], name=name)

    return wall


def vertical_wall_with_aperture(
    width: float,
    height: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_vec: tuple[float, float, float] = (0.0, 0.0, 1.0),
    rot_angle: float = 0.0,
    name: str | None = None,
    aperture_width: float = 0.0,
    aperture_height: float = 0.0,
    aperture_xz_offset: tuple[float, float] = (0.0, 0.0),
) -> Wall:
    """Create a Wall with an aperture.

    By default, the wall is vertical and located on the XZ plane
    with the normal pointing towards (0, 1, 0).

    Order of transformations:
    - create a wall with the first vertex at (0, 0, 0)
    - apply rotation
    - apply translation

    The aperture is located at the point `aperture_xz_offset` relative to the `p0` point.
    The `p0` point is located at (0, 0, 0) by default (unless the `translate` parameter is used).

    Args:
        width: Width of the wall
        height: Height of the wall
        translate: Origin of the wall
        rot_vec: Vector describing the rotation of the wall
        rot_angle: Angle of the rotation (in radians)
        name: Name of the wall (random if None)
        aperture_width: Width of the aperture
        aperture_height: Height of the aperture
        aperture_xz_offset: Offset of the aperture in the XZ plane from the the p0 point

    Return:
        Wall
    """
    vec = np.array(rot_vec)

    # Make wall points
    p0 = Point(0, 0, 0)
    p1 = Point(0, 0, height)
    p2 = Point(width, 0, height)
    p3 = Point(width, 0, 0)

    # Make aperture points
    ap0 = p0 + (aperture_xz_offset[0], 0, aperture_xz_offset[1])
    ap1 = ap0 + (0, 0, aperture_height)
    ap2 = ap1 + (aperture_width, 0, 0)
    ap3 = ap2 + (0, 0, -aperture_height)

    if rot_angle != 0:
        # Rotate wall points
        (p0, p1, p2, p3), _ = rotate_points_around_vector(
            points=[p0, p1, p2, p3],
            u=vec,
            phi=rot_angle,
        )
        # Rotate aperture points
        (ap0, ap1, ap2, ap3), _ = rotate_points_around_vector(
            points=[ap0, ap1, ap2, ap3],
            u=vec,
            phi=rot_angle,
        )

    # Move wall points
    p0 += translate
    p1 += translate
    p2 += translate
    p3 += translate

    # Move aperture points
    ap0 += translate
    ap1 += translate
    ap2 += translate
    ap3 += translate

    # Create main polygon
    poly = Polygon([p0, p1, p2, p3], name=name)

    # Create subpolygon
    subpoly = Polygon([ap0, ap1, ap2, ap3], name=poly.name + "-sub")

    wall = Wall([poly], name=name)
    wall.add_polygon(subpoly, parent=poly.name)

    return wall


if __name__ == "__main__":
    # Example
    w1 = vertical_wall_with_aperture(
        width=2.0,
        height=1.0,
        translate=(0, 0, 0),
        rot_vec=(0, 0, 0),
        rot_angle=0,
        aperture_width=1.0,
        aperture_height=0.5,
        aperture_xz_offset=(0.5, 0.25),
    )

    w2 = vertical_wall(
        width=2.0,
        height=1.0,
        translate=(0, 0, 0),
        rot_vec=(0, 0, 1),
        rot_angle=np.pi / 4.0,
    )

    w3 = vertical_wall(
        width=2.0,
        height=1.0,
        translate=(0, 0, 0),
        rot_vec=(0, 0, 1),
        rot_angle=-np.pi / 4.0,
    )

    plot_objects((w1, w2, w3))
