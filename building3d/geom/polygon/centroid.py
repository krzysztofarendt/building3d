from numba import njit
import numpy as np

from building3d.geom.types import PointType, IndexType, FLOAT
from building3d.geom.triangles import triangle_centroid
from building3d.geom.triangles import triangle_area


@njit
def polygon_centroid(pts: PointType, tri: IndexType) -> PointType:
    """Calculates the center of mass of a polygon.

    The centroid is calculated using a weighted average of
    the triangle centroids. The weights are the triangle areas.

    Uses triangles from `triangles.triangulate()`.
    """
    num_tri = tri.shape[0]
    assert num_tri > 0, "No triangles passed"

    tri_ctr = np.zeros((num_tri, 3), dtype=FLOAT)
    weights = np.zeros(num_tri, dtype=FLOAT)

    for i in range(num_tri):
        tri_ctr[i] = triangle_centroid(pts[tri[i, 0]], pts[tri[i, 1]], pts[tri[i, 2]])
        weights[i] = triangle_area(pts[tri[i, 0]], pts[tri[i, 1]], pts[tri[i, 2]])

    poly_ctr = np.zeros(3, dtype=FLOAT)
    for i in range(num_tri):
        poly_ctr += tri_ctr[i] * weights[i]

    return poly_ctr
