import logging

import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.points import is_point_in_array
from building3d.geom.numba.points import points_equal
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.rotation import rotate_points_around_vector
from building3d.geom.numba.types import FLOAT


logger = logging.getLogger(__name__)


def floor_plan(
    plan: list[tuple[float, float]] | list[tuple[int, int]],
    height: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_angle: float = 0.0,
    name: str | None = None,
    wall_names: list[str] | None = None,
    floor_name: str = "floor",
    ceiling_name: str = "ceiling",
) -> Solid:
    """Make a solid volume from a floor plan (list of (x, y) points).

    If wall_names is not provided, the names will be "wall-0", "wall-1", etc.
    If floor_name and ceiling_name are not provided, they will be "floor" and "ceiling".

    Args:
        plan: list of (x, y) points
        height: height of the zone
        translate: translation vector
        rot_angle: rotation angle in radians
        name: name of the zone
        wall_names: names of the walls
        floor_name: name of the floor
        ceiling_name: name of the ceiling

    Return:
        Solid
    """
    # Define the rotation vector (it is hardcoded, floor and ceiling must be horizontal)
    rot_vec = np.array([0.0, 0.0, 1.0], dtype=FLOAT)

    # Prepare wall names
    if wall_names is None:
        wall_names = [f"wall-{i}" for i in range(len(plan))]
    else:
        if len(wall_names) != len(plan):
            raise ValueError(
                "Number of wall names must be equal to the number of points in the plan"
            )
        if len(set(wall_names)) != len(wall_names):
            raise ValueError("Wall names must be unique")

    # Set up floor and ceiling Points
    floor_pts = np.vstack([new_point(float(x), float(y), 0.0) for x, y in plan])
    ceiling_pts = np.vstack([new_point(float(x), float(y), float(height)) for x, y in plan])

    # Rotate
    if not np.isclose(rot_angle, 0):
        floor_pts, _ = rotate_points_around_vector(
            pts = floor_pts,
            u = rot_vec,
            phi = rot_angle,
        )
        ceiling_pts, _ = rotate_points_around_vector(
            pts = ceiling_pts,
            u = rot_vec,
            phi = rot_angle,
        )

    # Translate
    if not np.allclose(translate, (0, 0, 0)):
        floor_pts = np.vstack([p + translate for p in floor_pts])
        ceiling_pts = np.vstack([p + translate for p in ceiling_pts])
        z0 = translate[2]
    else:
        z0 = 0

    # Make Polygons (and subpolygons) and Walls
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

        poly = Polygon(np.vstack([p0, p1, p2, p3]), name=wall_names[i])
        wall = Wall([poly], name=wall_names[i])

        walls.append(wall)

    floor_poly = Polygon(floor_pts, name=floor_name)
    # Floor's normal should point downwards
    if not np.allclose(floor_poly.vn, [0, 0, -1]):
        floor_poly = floor_poly.flip()

    ceiling_poly = Polygon(ceiling_pts, name=ceiling_name)
    # Ceiling's normal should point upwards
    if not np.allclose(ceiling_poly.vn, [0, 0, 1]):
        ceiling_poly = ceiling_poly.flip()

    floor = Wall([floor_poly], name=floor_name)
    ceiling = Wall([ceiling_poly], name=ceiling_name)

    # Make sure all polygon normals point outwards the zone.
    # Compare the order of wall vertices to the order
    # of floor vertices - they should be opposite.
    for k in range(len(walls)):
        w_poly = walls[k].get_polygons()[0]  # There is only one
        w_pts = w_poly.pts
        f_poly = floor.get_polygons()[0]  # There is only one
        f_pts = f_poly.pts

        wall_z0_pts = []
        for i in range(len(w_pts)):
            if w_pts[i, -1] == z0:
                wall_z0_pts.append(w_pts[i])

        wall_z0_pts = np.array(wall_z0_pts)

        floor_adjacent_pts = []

        prev_taken = None
        for i in range(len(f_pts)):
            if is_point_in_array(f_pts[i], wall_z0_pts):
                floor_adjacent_pts.append(f_pts[i])
                if prev_taken is None:
                    prev_taken = i
                elif prev_taken != i - 1:
                    # Need to flip the list, because the first and last points
                    # were taken and they are now in the wrong order
                    floor_adjacent_pts.reverse()

            if len(floor_adjacent_pts) == 2:
                break

        if (
            points_equal(wall_z0_pts[0], floor_adjacent_pts[1]) and
            points_equal(wall_z0_pts[1], floor_adjacent_pts[0])
        ):
            # Direction is OK
            pass
        else:
            # Need to reverse the order of polygon vertices
            walls[k].replace_polygon(w_poly.name, w_poly.flip(new_name=w_poly.name))
            logger.debug(f"Wall vertices reversed {walls[k].name}")

    # Add floor and ceiling
    walls.append(floor)
    walls.append(ceiling)

    # Make a solid and return
    solid = Solid(walls, name=name)

    return solid
