from numba import njit

from building3d.config import GEOM_ATOL
from building3d.geom.polygon.ispointinside import is_point_inside_projection
from building3d.geom.types import PointType, VectorType, IndexType


@njit
def find_target_surface(
    # Ray position and direction
    pos: PointType,
    direction: VectorType,
    # Polygon vertices and faces, each list element contains an array defining a polygon
    poly_pts: list[PointType],
    poly_tri: list[IndexType],
    # Which polygons to check and which to neglect
    transparent_polygons: set[int],
    polygons_to_check: set[int],
    atol: float = GEOM_ATOL,
) -> int:
    """Find the target surface for a ray at position `pos` going along `direction`.

    Transparent polygons are ignored.
    The function checks only the polygons from the set `polygons_to_check`.

    Args:
        pos: The starting position of the ray.
        direction: The direction vector of the ray.
        poly_pts: List of polygon vertices, where each element is an array defining a polygon.
        poly_tri: List of polygon faces, corresponding to the poly_pts.
        transparent_polygons: Set of indices for polygons to be considered transparent.
        polygons_to_check: Set of indices for polygons to be checked for intersection.

    Returns:
        int: The index of the target surface (polygon) hit by the ray, or -1 if no surface is hit.
    """
    for pn in polygons_to_check:
        if pn in transparent_polygons:
            continue

        if is_point_inside_projection(
            pos, direction, poly_pts[pn], poly_tri[pn], fwd_only=True, atol=atol
        ):
            return pn

    return -1
