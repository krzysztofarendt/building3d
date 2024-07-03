import logging
from collections import defaultdict

import numpy as np

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.solid import Solid
from building3d.geom.rotate import rotate_points_around_vector
from building3d.geom.line import create_point_between_2_points_at_distance


logger = logging.getLogger(__name__)


def floor_plan(
    plan: list[tuple[float, float]] | list[tuple[int, int]],
    height: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_angle: float = 0.0,
    name: str | None = None,
    wall_names: list[str] = [],
    floor_name: str = "floor",
    ceiling_name: str = "ceiling",
    apertures: dict[str, tuple[str, float, float, float, float]] = {},
) -> Solid:
    """Make a solid volume from a floor plan (list of (x, y) points).

    If wall_names is not provided, the names will be "wall-0", "wall-1", etc.
    If floor_name and ceiling_name are not provided, they will be "floor" and "ceiling".
    Aperture generation is supported only for the vertical walls.

    Args:
        plan: list of (x, y) points
        height: height of the zone
        translate: translation vector
        rot_angle: rotation angle
        name: name of the zone
        wall_names: names of the walls
        floor_name: name of the floor
        ceiling_name: name of the ceiling
        apertures: dict of {aperture_name: (wall_name, center, bottom, width, height)}

    Return:
        Solid
    """
    # Define the rotation vector (it is hardcoded, floor and ceiling must be horizontal)
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

    # Set up aperture Points
    aperture_pts = {}
    aperture_parent_walls = defaultdict(list)

    for ap_name in apertures.keys():
        wall_name = apertures[ap_name][0]
        ap_center = apertures[ap_name][1]  # Relative center axis (w.r.t. wall width)
        ap_bottom = apertures[ap_name][2]  # Relative bottom axis (w.r.t. wall height)
        ap_width = apertures[ap_name][3]   # Relative width (w.r.t. wall width)
        ap_height = apertures[ap_name][4]  # Relative height (w.r.t. wall height)

        aperture_parent_walls[wall_name].append(ap_name)

        # Find wall floor points
        wall_num = -1
        for i in range(len(wall_names)):
            if wall_name == wall_names[i]:
                wall_num = i
                break
        if wall_num < 0:
            raise ValueError(f"Wall name not found: {wall_name}")

        left_index = wall_num
        right_index = wall_num + 1 if wall_num + 1 < len(wall_names) else 0

        wall_left_pt = floor_pts[left_index]
        wall_right_pt = floor_pts[right_index]

        left = create_point_between_2_points_at_distance(
            p1 = wall_left_pt,
            p2 = wall_right_pt,
            distance = ap_center - ap_width / 2,
        )
        right = create_point_between_2_points_at_distance(
            p1 = wall_left_pt,
            p2 = wall_right_pt,
            distance = ap_center + ap_width / 2,
        )

        vert_offset = height * ap_bottom  # Wall's height * relative position of the bottom
        abs_height = height * ap_height  # Wall's height * relative height of aperture

        ap_p0 = left + (0, 0, vert_offset)
        ap_p1 = left + (0, 0, vert_offset + abs_height)
        ap_p2 = right + (0, 0, vert_offset + abs_height)
        ap_p3 = right + (0, 0, vert_offset)

        aperture_pts[ap_name] = [wall_name, [ap_p0, ap_p1, ap_p2, ap_p3]]

    # Rotate
    if not np.isclose(rot_angle, 0):
        floor_pts, _ = rotate_points_around_vector(
            points = floor_pts,
            u = rot_vec,
            phi = rot_angle,
        )
        ceiling_pts, _ = rotate_points_around_vector(
            points = ceiling_pts,
            u = rot_vec,
            phi = rot_angle,
        )
        for ap_name in aperture_pts.keys():
            original_points = aperture_pts[ap_name][1]
            rotated_points, _ = rotate_points_around_vector(
                points = original_points,
                u = rot_vec,
                phi = rot_angle,
            )
            aperture_pts[ap_name][1] = rotated_points

    # Translate
    if not np.isclose(translate, (0, 0, 0)).all():
        floor_pts = [p + translate for p in floor_pts]
        ceiling_pts = [p + translate for p in ceiling_pts]
        z0 = translate[2]

        for ap_name in aperture_pts.keys():
            original_points = aperture_pts[ap_name][1]
            translated_points = [p + translate for p in original_points]
            aperture_pts[ap_name][1] = translated_points
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

        poly = Polygon([p0, p1, p2, p3], name=wall_names[i])
        wall = Wall([poly], name=wall_names[i])

        # Subpolygons?
        if wall_names[i] in aperture_parent_walls.keys():

            # Collect apertures for this wall
            apertures_for_this_wall = aperture_parent_walls[wall_names[i]]

            for ap_name in apertures_for_this_wall:
                ap_p0, ap_p1, ap_p2, ap_p3 = aperture_pts[ap_name][1]
                subpoly = Polygon([ap_p0, ap_p1, ap_p2, ap_p3], name=ap_name)

                wall.add_polygon(subpoly, parent=wall_names[i])

        walls.append(wall)

    floor_poly = Polygon(floor_pts, name=floor_name)
    # Floor's normal should point downwards
    if not np.isclose(floor_poly.normal, [0, 0, -1]).all():
        floor_poly = floor_poly.flip()

    ceiling_poly = Polygon(ceiling_pts, name=ceiling_name)
    # Ceiling's normal should point upwards
    if not np.isclose(ceiling_poly.normal, [0, 0, 1]).all():
        ceiling_poly = ceiling_poly.flip()

    floor = Wall([floor_poly], name=floor_name)
    ceiling = Wall([ceiling_poly], name=ceiling_name)

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
            if w_pts[i].z == z0:
                wall_z0_pts.append(w_pts[i])

        floor_adjacent_pts = []

        prev_taken = None
        for i in range(len(f_pts)):
            if f_pts[i] in wall_z0_pts:
                floor_adjacent_pts.append(f_pts[i])
                if prev_taken is None:
                    prev_taken = i
                else:
                    if prev_taken != i - 1:
                        # Need to flip the list, because the first and last points
                        # were taken and they are now in the wrong order
                        floor_adjacent_pts.reverse()

            if len(floor_adjacent_pts) == 2:
                break

        if wall_z0_pts[0] == floor_adjacent_pts[1] and wall_z0_pts[1] == floor_adjacent_pts[0]:
            # Direction is OK
            pass
        else:
            # Need to reverse the order of polygon vertices
            w_poly = w_poly.flip()
            wall_name = walls[k].name
            walls[k] = Wall([w_poly], name=wall_name)
            logger.debug(f"Wall vertices reversed {wall_name}")

    # Make sure aperture normals are same as parent polygon normals
    for k in range(len(walls)):
        poly_name = walls[k].get_polygon_names()[0]
        poly_normal = walls[k].get_polygons()[0].normal

        to_flip = []
        for subpoly in walls[k].get_subpolygons(poly_name):
            if not np.isclose(subpoly.normal, poly_normal).all():
                to_flip.append(subpoly.name)

        for subpoly_name in to_flip:
            walls[k].polygons[subpoly_name] = walls[k].polygons[subpoly_name].flip()

    # Add floor and ceiling
    walls.append(floor)
    walls.append(ceiling)

    # Make a solid and return
    solid = Solid(walls, name=name)

    return solid
