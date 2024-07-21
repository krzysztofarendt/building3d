import logging

import numpy as np

from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.object_path import split_path
from building3d.geom.paths import PATH_SEP


logger = logging.getLogger(__name__)


def find_target(
    position: Point,
    velocity: np.ndarray,
    location: str,
    building: Building,
    transparent: list[str],
    checked_locations: set,
) -> str:
    """Find target surface for a moving particle in a building.

    This is a recursive function. If the target surface is in
    the `transparent` list, it checks the adjacent solid recursively.

    Args:
        position: particle poisition
        velocity: particle velocity
        location: particle location (path to solid)
        building: building containing the solid
        transparent: list of transparent polygons (paths to polygons)
        checked_locations: set of solids that were already checked

    Return:
        path to the polygon that the particle is moving towards
    """
    logger.debug(f"Called find_target({position=}, {velocity=}, {location=}, {building=}, {transparent=})")
    target_surface = ""

    found = False
    zname, sname = split_path(location)
    z = building.zones[zname]
    s = z.solids[sname]
    logger.debug(f"{location=}")

    for w in s.get_walls():
        for p in w.get_polygons():
            logger.debug(f"Checking {p=}")
            if p.is_point_inside_projection(position, velocity):
                poly_path = object_path(z, s, w, p)
                logger.debug(f"Particle will hit this polygon: {poly_path}")

                if poly_path in transparent:
                    # Recursively search adjacent solids
                    logger.debug("...but it's transparent! Have to look into adjacent solid.")
                    adj_poly = building.get_graph()[poly_path]
                    adj_z, adj_s, _, _ = split_path(adj_poly)
                    new_location = adj_z + PATH_SEP + adj_s

                    if new_location not in checked_locations:
                        checked_locations.add(location)
                        return find_target(
                            position,
                            velocity,
                            new_location,
                            building,
                            transparent,
                            checked_locations,
                        )

                else:
                    target_surface = object_path(zone=z, solid=s, wall=w, poly=p)
                    found = True
                    break
        if found:
            break

    if not found:
        raise RuntimeError("Particle isn't moving towards any surface")

    assert len(target_surface) > 0

    return target_surface
