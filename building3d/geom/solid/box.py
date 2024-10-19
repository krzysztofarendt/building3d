import numpy as np

from building3d.geom.points import new_point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.types import FLOAT
from building3d.geom.wall import Wall


def box(
    x: float,
    y: float,
    z: float,
    move: tuple[float, float, float] = (0.0, 0.0, 0.0),
    name: str | None = None,
) -> Solid:
    """Return a solid with given dimensions and location.

    `x` is the dimension along the X axis.
    `y` is the dimension along the Y axis.
    `z` is the dimension along the Z axis.

    Rotation is currently not supported.

    The corner `(min(x), min(y), min(z))` will be located at `move`.

    The polygon and wall names are hardcoded:
    - floor
    - wall_0 (XZ at ymin)
    - wall_1 (YZ at xmax)
    - wall_2 (XZ at ymax)
    - wall_3 (YZ at xmin)
    - roof

    The solid will be named `name` (random if not given).
    """
    # TODO: Add rotation

    stretch = np.array((x, y, z), dtype=FLOAT)
    mv = np.array(move)

    p0 = new_point(0.0, 0.0, 0.0) * stretch + mv
    p1 = new_point(1.0, 0.0, 0.0) * stretch + mv
    p2 = new_point(1.0, 1.0, 0.0) * stretch + mv
    p3 = new_point(0.0, 1.0, 0.0) * stretch + mv
    p4 = new_point(0.0, 0.0, 1.0) * stretch + mv
    p5 = new_point(1.0, 0.0, 1.0) * stretch + mv
    p6 = new_point(1.0, 1.0, 1.0) * stretch + mv
    p7 = new_point(0.0, 1.0, 1.0) * stretch + mv

    poly_fl = Polygon(np.vstack((p0, p3, p2, p1)), name="floor")
    poly_w0 = Polygon(np.vstack((p0, p1, p5, p4)), name="poly_0")
    poly_w1 = Polygon(np.vstack((p1, p2, p6, p5)), name="poly_1")
    poly_w2 = Polygon(np.vstack((p3, p7, p6, p2)), name="poly_2")
    poly_w3 = Polygon(np.vstack((p0, p4, p7, p3)), name="poly_3")
    poly_rf = Polygon(np.vstack((p4, p5, p6, p7)), name="ceiling")

    wall_fl = Wall([poly_fl], name="floor")
    wall_w0 = Wall([poly_w0], name="wall_0")
    wall_w1 = Wall([poly_w1], name="wall_1")
    wall_w2 = Wall([poly_w2], name="wall_2")
    wall_w3 = Wall([poly_w3], name="wall_3")
    wall_rf = Wall([poly_rf], name="ceiling")

    solid = Solid(
        walls=[wall_fl, wall_w0, wall_w1, wall_w2, wall_w3, wall_rf], name=name
    )

    return solid
