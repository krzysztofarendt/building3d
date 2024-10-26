from numba import njit
import numpy as np

from building3d.config import GEOM_ATOL
from building3d.geom.polygon.ispointinside import is_point_inside_projection
from building3d.geom.polygon.distance import distance_point_to_polygon
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.types import VectorType
from building3d.geom.vectors import normal


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

    NOTE:
        `transparent_polygons` and `polygons_to_check` cannot be empty sets if JIT is used.
        `set([-1])` is a good substitute for an empty set.

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
    # Key -> polygon number
    # Value -> polygon distance to ray's position (pos)
    target_candidates = {-1: np.inf}  # Initialize with dummy data for numba to know the types
    min_dist_index = -1

    for pn in polygons_to_check:
        if pn in transparent_polygons:
            continue

        if is_point_inside_projection(
            pos, direction, poly_pts[pn], poly_tri[pn], fwd_only=True, atol=atol
        ):
            # Calculate polygon normal vector using the assumption that
            # the first vector is convex
            polygon_normal = normal(poly_pts[pn][-1], poly_pts[pn][0], poly_pts[pn][1])

            # Calculate how far the ray is from this polygon
            dist = distance_point_to_polygon(pos, poly_pts[pn], poly_tri[pn], polygon_normal)
            target_candidates[pn] = dist

            if min_dist_index < 0:
                # It is the first polygon that is being checked...
                min_dist_index = pn

            # If it is the closest polygon so far -> remember it
            if dist < target_candidates[min_dist_index]:
                min_dist_index = pn

    if min_dist_index < 0:
        return -1
    else:
        return min_dist_index
