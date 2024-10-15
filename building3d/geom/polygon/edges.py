import numpy as np
from numba import njit

from building3d.geom.types import FLOAT
from building3d.geom.types import PointType


@njit
def polygon_edges(pts: PointType) -> PointType:
    """Returns edges of this polygon as an array shaped (num_edges, 2, 3).

    An edge is a sequence of 2 points.

    Args:
        pts: points array, shape (num_points, 3)

    Returns:
        edges array, shape (num_edges, 2, 3)
    """
    edges_list = []
    edge = np.zeros((2, 3), dtype=FLOAT)

    num_pts = pts.shape[0]
    i = 0
    j = 0
    while i < num_pts:
        edge[j] = pts[i]
        i += 1
        j += 1
        if j == 2:
            edges_list.append(edge.copy())
            i -= 1
            j = 0

    edge[0] = pts[-1]
    edge[1] = pts[0]
    edges_list.append(edge.copy())

    num_edges = len(edges_list)
    edges_arr = np.zeros((num_edges, 2, 3), dtype=FLOAT)
    for i in range(num_edges):
        edges_arr[i, :, :] = edges_list[i]

    return edges_arr
