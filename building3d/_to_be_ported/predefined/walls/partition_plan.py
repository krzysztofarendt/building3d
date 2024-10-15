import logging

import numpy as np

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.rotate import rotate_points_around_vector
from building3d.geom.wall import Wall

logger = logging.getLogger(__name__)


def partition_plan(
    plan: list[tuple[float, float]] | list[tuple[int, int]],
    height: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_angle: float = 0.0,
    wall_names: list[str] = [],
) -> list[Wall]:
    """Return a list of vertical walls based on a list of x, y points and height.

    This function can be used to create internal walls for a solid (partitions)
    or to create external shading elements.
    """
    # Define the rotation vector (it is hardcoded, walls must be vertical)
    rot_vec = np.array([0.0, 0.0, 1.0])

    # Prepare wall names
    if len(wall_names) == 0:
        wall_names = [f"wall-{i}" for i in range(len(plan))]
    else:
        if len(wall_names) != len(plan):
            raise ValueError(
                "Number of wall names must be equal to the number of points in the plan"
            )
        if len(set(wall_names)) != len(wall_names):
            raise ValueError("Wall names must be unique")

    # Set up floor and ceiling Points
    floor_pts = [Point(float(x), float(y), 0.0) for x, y in plan]
    ceiling_pts = [Point(float(x), float(y), float(height)) for x, y in plan]

    # Rotate
    if not np.isclose(rot_angle, 0):
        floor_pts, _ = rotate_points_around_vector(
            points=floor_pts,
            u=rot_vec,
            phi=rot_angle,
        )
        ceiling_pts, _ = rotate_points_around_vector(
            points=ceiling_pts,
            u=rot_vec,
            phi=rot_angle,
        )

    # Translate
    if not np.isclose(translate, (0, 0, 0)).all():
        floor_pts = [p + translate for p in floor_pts]
        ceiling_pts = [p + translate for p in ceiling_pts]

    # Make Polygons (and subpolygons) and Walls
    walls = []
    for i in range(len(plan) - 1):
        ths = i  # This point
        nxt = ths + 1  # Next point

        p0 = floor_pts[ths]
        p1 = floor_pts[nxt]
        p2 = ceiling_pts[nxt]
        p3 = ceiling_pts[ths]

        poly = Polygon([p0, p1, p2, p3], name=wall_names[i])
        wall = Wall([poly], name=wall_names[i])
        walls.append(wall)

    return walls
