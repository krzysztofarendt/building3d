from numba import njit
import numpy as np

from building3d.geom.numba.points import points_equal
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.exceptions import GeometryError
from building3d.geom.numba.polygon.distance import distance_point_to_edge
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from .constants import EXTERIOR, INTERIOR, VERTEX, EDGE, INVALID_INDEX


@njit
def locate_slicing_points(
    slicing_pts: PointType,
    pts: PointType,
    tri: IndexType,
    edges: PointType,
) -> list[tuple[int, int]]:
    """Returns the location of each slicing point.

    Args:
        slicing_pts: points defining how to slice the polygon
        pts: polygon points
        tri: polygon triangles
        poly_edges: list of tuples of points defining the polygon edges

    Return:
        list of tuples defining the location of each slicing point
    """
    if len(slicing_pts) == 0:
        raise GeometryError("No slicing points passed")

    loc = []
    for ptest in slicing_pts:
        loc.append(locate_point_on_polygon(ptest, pts, tri, edges))

    return loc


@njit
def locate_point_on_polygon(ptest, pts, tri, edges) -> tuple[int, int]:
    """Return a tuple defining the location of `ptest` inside the polygon.

    Possible return values:
    - `(EXTERIOR, INVALID_INDEX)` - the point is outside the polygon
    - `(INTERIOR, INVALID_INDEX)` - inside the polygon, not touching any vertex or edge
    - `(VERTEX, vi)` - touching a vertex with index `vi`
    - `(EDGE, ei)` - touching an edge with index `ei`

    The constants `EXTERIOR`, `INTERIOR`, `VERTEX`, `EDGE`, `INVALID_INDEX`
    are defined in `./constants.py`.
    """
    if not is_point_inside(ptest, pts, tri):
        return (EXTERIOR, INVALID_INDEX)
    else:
        for i, p in enumerate(pts):
            if points_equal(ptest, p):
                return (VERTEX, i)

        for i, ed in enumerate(edges):
            d_to_edge = distance_point_to_edge(ptest, ed[0], ed[1])
            if np.isclose(d_to_edge, 0):
                return (EDGE, i)

        return (INTERIOR, INVALID_INDEX)
