from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid


def box(
    x: float,
    y: float,
    z: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    name: str | None = None,
) -> Zone:
    """Return a zone with given dimensions, located at translate.

    `x` is the dimension along the X axis.
    `y` is the dimension along the Y axis.
    `z` is the dimension along the Z axis.

    Rotation is currently not supported.

    The corner `(min(x), min(y), min(z))` will be located at `translate`.

    The polygon and wall names are hardcoded:
    - floor
    - wall-0
    - wall-1
    - wall-2
    - wall-3
    - roof

    Both, the solid and the zone are named `name` (random if not given).
    """
    # TODO: Add rotation

    stretch = (x, y, z)
    p0 = Point(0.0, 0.0, 0.0) * stretch + translate
    p1 = Point(1.0, 0.0, 0.0) * stretch + translate
    p2 = Point(1.0, 1.0, 0.0) * stretch + translate
    p3 = Point(0.0, 1.0, 0.0) * stretch + translate
    p4 = Point(0.0, 0.0, 1.0) * stretch + translate
    p5 = Point(1.0, 0.0, 1.0) * stretch + translate
    p6 = Point(1.0, 1.0, 1.0) * stretch + translate
    p7 = Point(0.0, 1.0, 1.0) * stretch + translate

    poly_fl = Polygon([p0, p3, p2, p1], name=f"floor")
    poly_w0 = Polygon([p0, p1, p5, p4], name=f"wall-0")
    poly_w1 = Polygon([p1, p2, p6, p5], name=f"wall-1")
    poly_w2 = Polygon([p3, p7, p6, p2], name=f"wall-2")
    poly_w3 = Polygon([p0, p4, p7, p3], name=f"wall-3")
    poly_rf = Polygon([p4, p5, p6, p7], name=f"roof")

    wall_fl = Wall([poly_fl], name=f"floor")
    wall_w0 = Wall([poly_w0], name=f"wall-0")
    wall_w1 = Wall([poly_w1], name=f"wall-1")
    wall_w2 = Wall([poly_w2], name=f"wall-2")
    wall_w3 = Wall([poly_w3], name=f"wall-3")
    wall_rf = Wall([poly_rf], name=f"roof")

    solid = Solid(walls=[wall_fl, wall_w0, wall_w1, wall_w2, wall_w3, wall_rf], name=name)
    zone = Zone(name=name)
    zone.add_solid(solid)

    return zone
