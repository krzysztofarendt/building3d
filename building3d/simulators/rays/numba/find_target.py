import logging

from building3d.geom.numba.building import Building
from building3d.geom.numba.polygon.ispointinside import is_point_inside_projection
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.types import PointType, VectorType

from building3d.geom.paths.object_path import split_path
from building3d.geom.paths import PATH_SEP


logger = logging.getLogger(__name__)


def find_target(
    pos: PointType,
    vel: VectorType,
    loc: str,
    bdg: Building,
    trans: set[str],
    chk: set[str],
) -> str:
    """Find target surface for a moving particle in a building.

    This is a recursive function. If the target surface is in
    the `transparent` list, it checks the adjacent solids recursively.

    Args:
        pos: particle poisition
        vel: particle velocity
        loc: location to search (path to solid)
        bdg: building containing the solid
        trans: set of transparent polygons (paths to polygons)
        chk: set of solids that were already checked

    Return:
        path to the polygon that the particle is moving towards
    """
    logger.debug(
        f"Called find_target({pos=}, {vel=}, {loc=}, {bdg=}, {trans=})"
    )
    trg_surf = ""

    # Find transparent surfaces


    found = False
    path = split_path(loc)
    assert len(path) == 3, f"Incorrect path length ({len(path)}). Should be 3."

    bname, zname, sname = path
    assert bname == bdg.name, "Building names do not match"

    z = bdg.zones[zname]
    s = z.solids[sname]
    logger.debug(f"{loc=}")

    for w in s.walls.values():
        for p in w.polygons.values():
            logger.debug(f"Checking {p=}")

            if is_point_inside_projection(ptest=pos, v=vel, pts=p.pts, tri=p.tri, fwd_only=True):
                poly_path = PATH_SEP.join((bname, z.name, s.name, w.name, p.name))
                logger.debug(f"Particle will hit this polygon: {poly_path}")

                if poly_path in trans:
                    # Recursively search adjacent solids
                    logger.debug("Polygon is transparent. Need to look into adjacent solid.")

                    adj_polygons = bdg.get_graph()[poly_path]
                    assert len(adj_polygons) == 1, "If polygon is transparent, it must be true"

                    adj_poly = adj_polygons[0]

                    bname, adj_z, adj_s, _, _ = split_path(adj_poly)
                    new_location = PATH_SEP.join((bname, adj_z, adj_s))

                    if new_location not in chk:
                        chk.add(loc)
                        return find_target(pos, vel, new_location, bdg, trans, chk)

                else:
                    trg_surf = PATH_SEP.join((bname, z.name, s.name, w.name, p.name))
                    found = True
                    break
        if found:
            break

    if not found:
        raise RuntimeError("Particle isn't moving towards any surface")

    assert len(trg_surf) > 0
    assert isinstance(bdg.get(trg_surf), Polygon)

    return trg_surf
