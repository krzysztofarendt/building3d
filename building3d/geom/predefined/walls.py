import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.rotate import rotate_points_around_vector


def wall(
    width: float,
    height: float,
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_vec: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_angle: float = 0.0,
    name: str | None = None,
) -> Wall:
    """Create a Wall with given dimensions, located at origin.

    Order of transformations:
    - create a wall with the first vertex at (0, 0, 0)
    - apply rotation
    - apply translation

    Args:
        width: Width of the wall
        height: Height of the wall
        origin: Origin of the wall
        rot_vec: Vector describing the rotation of the wall
        rot_angle: Angle of the rotation (in radians)
        name: Name of the wall (random if None)

    Return:
        Wall
    """
    vec = np.array(rot_vec)

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(width, 0.0, 0.0)
    p2 = Point(width, height, 0.0)
    p3 = Point(0.0, height, 0.0)

    if rot_angle != 0:
        (p0, p1, p2, p3), _ = rotate_points_around_vector(
            points = [p0, p1, p2, p3],
            u = vec,
            phi = rot_angle,
        )

    p0 += origin
    p1 += origin
    p2 += origin
    p3 += origin

    poly = Polygon([p0, p1, p2, p3], name=name)
    wall = Wall([poly], name=name)
    return wall



def wall_with_aperture(
    width: float,
    height: float,
    aperture_width: float,
    aperture_height: float,
    aperture_xy_offset: tuple[float, float],
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
    name: str = "",
) -> Wall:
    ...


if __name__ == "__main__":
    w1 = wall(
        width=2.0,
        height=1.0,
        origin=(0.0, 0.0, 0.0),
        rot_vec=(0.0, 0.0, 0.0),
        rot_angle=0.0,
    )

    w2 = wall(
        width=2.0,
        height=1.0,
        origin=(0.0, 0.0, 0.0),
        rot_vec=(0.0, 1.0, 0.0),
        rot_angle=np.pi / 4.0,
    )

    w3 = wall(
        width=2.0,
        height=1.0,
        origin=(0.0, 0.0, 0.0),
        rot_vec=(0.0, 1.0, 0.0),
        rot_angle=-np.pi / 4.0,
    )

    plot_objects(w1, w2, w3)
