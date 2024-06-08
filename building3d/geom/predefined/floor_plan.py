import logging

import numpy as np

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone


logger = logging.getLogger(__name__)


def floor_plan(
    plan: list[tuple[float, float]],
    height: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_vec: tuple[float, float, float] = (0.0, 0.0, 1.0),
    rot_angle: float = 0.0,
    name: str | None = None,
) -> Zone:
    """Make a zone from a floor plan (list of (x, y) points)."""

    # TODO: translation
    # TODO: rotation
    # TODO: controllable wall names

    plan = [(float(x), float(y)) for x, y in plan]

    floor_pts = [Point(x, y, 0.0) for x, y in plan]
    ceiling_pts = [Point(x, y, height) for x, y in plan]

    walls = []
    for i in range(len(plan)):
        ths = i  # This point
        nxt = ths + 1  # Next point
        if nxt >= len(plan):
            nxt = 0

        p0 = floor_pts[ths]
        p1 = floor_pts[nxt]
        p2 = ceiling_pts[nxt]
        p3 = ceiling_pts[ths]

        poly = Polygon([p0, p1, p2, p3])
        wall = Wall([poly])
        walls.append(wall)

    floor_poly = Polygon(floor_pts)
    # Floor's normal should point downwards
    if not np.isclose(floor_poly.normal, [0, 0, -1]).all():
        floor_poly = floor_poly.flip()

    ceiling_poly = Polygon(ceiling_pts)
    # Ceiling's normal should point upwards
    if not np.isclose(ceiling_poly.normal, [0, 0, 1]).all():
        ceiling_poly = ceiling_poly.flip()

    floor = Wall([floor_poly])
    ceiling = Wall([ceiling_poly])

    # Make sure all polygon normals point outwards the zone.
    # Compare the order of wall vertices to the order
    # of floor vertices - they should be opposite.
    for k in range(len(walls)):
        w_poly = walls[k].get_polygons()[0]  # There is only one
        w_pts = w_poly.points
        f_poly = floor.get_polygons()[0]  # There is only one
        f_pts = f_poly.points

        wall_z0_pts = []
        for i in range(len(w_pts)):
            if w_pts[i].z == 0:
                wall_z0_pts.append(w_pts[i])

        floor_adjacent_pts = []
        for i in range(len(f_pts)):
            if f_pts[i] in wall_z0_pts:
                floor_adjacent_pts.append(f_pts[i])

            if len(floor_adjacent_pts) == 2:
                break

        if wall_z0_pts[0] == floor_adjacent_pts[1] and wall_z0_pts[1] == floor_adjacent_pts[0]:
            # Direction is OK
            pass
        else:
            # Need to reverse the order of polygon vertices
            w_poly = w_poly.flip()
            old_wall_name = walls[k].name
            walls[k] = Wall([w_poly])
            logger.debug(
                f"Wall vertices reversed. Old name: {old_wall_name}. New name: {walls[k].name}"
            )

    walls.append(floor)
    walls.append(ceiling)

    zone = Zone(name=name)
    zone.add_solid(name=name, walls=walls)

    return zone
