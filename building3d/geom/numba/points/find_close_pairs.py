import numpy as np
from numba import njit

from building3d.geom.numba.types import PointType, FLOAT
from building3d.geom.numba.points.visibility import are_points_visible
from building3d.geom.numba.polygon.edges import polygon_edges


@njit
def find_close_pairs(
    pts0: PointType,
    pts1: PointType,
    n: int,
    vis_only: bool = True,
) -> PointType:
    """Return an array of pairs of closest points between 2 polygons.

    The pairs are sorted based on distance in the ascending order.
    The number of pairs to return is n.
    Each point can be used once, i.e. each pair is unique.

    Args:
        pts0: Points of polygon 0
        pts1: Points of polygon 1
        n: Number of closest pairs to find
        vis_only: if True, will find only point pairs which are mutually visible

    Return:
        array shaped `(n, num_poly, xyz)`, where `num_poly=2` and `xyz=3`,
        the first item `[0, :, :]` is the closest pair of points

    Raises:
        ValueError: when `n` is too large and cannot find enough pairs
    """
    pairs = []

    edges0 = polygon_edges(pts0)
    edges1 = polygon_edges(pts1)

    for i, p0 in enumerate(pts0):
        for j, p1 in enumerate(pts1):
            if vis_only and not are_points_visible(p0, p1, edges0, edges1):
                continue
            else:
                d = np.linalg.norm(p1 - p0)
                pairs.append((d, i, j))

    pairs = sorted(pairs)
    used_0 = set()
    used_1 = set()

    indices = []

    for pp in pairs:
        _, i, j = pp
        if (i not in used_0) and (j not in used_1):
            indices.append((i, j))
            used_0.add(i)
            used_1.add(j)

    if len(indices) < n:
        raise ValueError("n is too large, not enough point pairs found")

    points = np.zeros((n, 2, 3), dtype=FLOAT)
    for k in range(n):
        points[k, 0] = pts0[indices[k][0]]
        points[k, 1] = pts1[indices[k][1]]

    return points
