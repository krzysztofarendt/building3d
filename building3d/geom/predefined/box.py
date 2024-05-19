from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone


def box(
    x: float,
    y: float,
    z: float,
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    name: str = "",
) -> Zone:
    """Return a zone with given dimensions, located at origin.

    `x` is the dimension along the X axis.
    `y` is the dimension along the Y axis.
    `z` is the dimension along the Z axis.

    Rotation is currently not supported.

    The corner `(min(x), min(y), min(z))` will be located at `origin`.
    """
    stretch = (x, y, z)
    p0 = Point(0.0, 0.0, 0.0) * stretch + origin
    p1 = Point(1.0, 0.0, 0.0) * stretch + origin
    p2 = Point(1.0, 1.0, 0.0) * stretch + origin
    p3 = Point(0.0, 1.0, 0.0) * stretch + origin
    p4 = Point(0.0, 0.0, 1.0) * stretch + origin
    p5 = Point(1.0, 0.0, 1.0) * stretch + origin
    p6 = Point(1.0, 1.0, 1.0) * stretch + origin
    p7 = Point(0.0, 1.0, 1.0) * stretch + origin

    if name != "":
        name = name + "-"
    name = name + random_id()

    poly_fl = Polygon([p0, p3, p2, p1], name=f"{name}-poly-floor")
    poly_w0 = Polygon([p0, p1, p5, p4], name=f"{name}-poly-wall0")
    poly_w1 = Polygon([p1, p2, p6, p5], name=f"{name}-poly-wall1")
    poly_w2 = Polygon([p3, p7, p6, p2], name=f"{name}-poly-wall2")
    poly_w3 = Polygon([p0, p4, p7, p3], name=f"{name}-poly-wall3")
    poly_rf = Polygon([p4, p5, p6, p7], name=f"{name}-poly-roof")

    wall_fl = Wall([poly_fl], name=f"{name}-wall-floor")
    wall_w0 = Wall([poly_w0], name=f"{name}-wall-wall0")
    wall_w1 = Wall([poly_w1], name=f"{name}-wall-wall1")
    wall_w2 = Wall([poly_w2], name=f"{name}-wall-wall2")
    wall_w3 = Wall([poly_w3], name=f"{name}-wall-wall3")
    wall_rf = Wall([poly_rf], name=f"{name}-wall-roof")

    zone = Zone(name=f"{name}-zone")
    zone.add_solid(
        name=f"{name}-solid",
        walls=[wall_fl, wall_w0, wall_w1, wall_w2, wall_w3, wall_rf],
    )

    return zone
