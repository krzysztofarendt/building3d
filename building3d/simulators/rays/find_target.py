import numpy as np

from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.object_path import split_path


def find_target(
    position: Point,
    velocity: np.ndarray,
    location: str,
    building: Building) -> str:
    """Find target surface for a moving particle in a building.

    Args:
        position: particle poisition
        velocity: particle velocity
        location: particle location (path to solid)
        building: building containing the solid

    Return:
        path to the polygon that the particle is moving towards
    """
    target_surface = ""

    found = False
    zname, sname = split_path(location)
    z = building.zones[zname]
    s = z.solids[sname]

    for w in s.get_walls():
        for p in w.get_polygons():
            if p.is_point_inside_projection(position, velocity):
                target_surface = object_path(zone=z, solid=s, wall=w, poly=p)
                found = True
                break
        if found:
            break

    if not found:
        raise RuntimeError("Particle isn't moving towards any surface")

    assert len(target_surface) > 0

    return target_surface
