from numba import njit
import numpy as np

from building3d.geom.numba.types import PointType, VectorType, IndexType, FLOAT
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.triangles import is_point_inside as is_point_inside_triangle
from building3d.geom.numba.polygon.edges import polygon_edges


@njit
def is_point_inside(
    ptest: PointType,
    pts: PointType,
    tri: IndexType,
) -> bool:
    """Checks whether a point lies on the surface of the polygon.

    Args:
        ptest: test point, array shape (3, )
        pts: polygon points, array shape (num_points, 3)
        tri: triangle indices, array shape (num_triangles, 3)

    Returns:
        True if ptest is inside the polygon
    """
    if not are_points_coplanar(np.vstack((pts, ptest.reshape((1, 3))))):
        return False

    # TODO: Sort triangles based on min. distance between ptest and tr. vertices/centroids
    ...

    num_tri = tri.shape[0]
    tri_pts = np.full((3, 3), np.nan, dtype=FLOAT)
    for i in range(num_tri):
        for j in range(3):
            tri_pts[j] = pts[tri[i, j]]

        if is_point_inside_triangle(ptest, tri_pts[0], tri_pts[1], tri_pts[2]):
            return True

    return False


def is_point_inside_margin(
    ptest: PointType,
    margin: float,
    pts: PointType,
    tri: IndexType,
) -> bool:
    """Checks whether a point lies within a polygon's inline.

    Returns `True` if:
    - point is inside the polygon and
    - distance from this point to the nearest edge is larger than `margin`

    Args:
        ptest: test point, array shape (3, )
        margin: distance from the boundary to the inline
        pts: polygon points, array shape (num_points, 3)
        tri: triangle indices, array shape (num_triangles, 3)

    Returns:
        True if ptest is inside the polygon at least `margin` far away from edges
    """
    inside = is_point_inside(ptest, pts, tri)
    if not inside:
        return False
    else:
        for edge in polygon_edges(pts):
            d = distance_point_to_edge(ptest, edge[0], edge[1])  # TODO
            if d < margin:
                return False
    return True


def is_point_inside_ortho_projection(
    ptest: PointType,
    pts: PointType,
    tri: IndexType,
) -> bool:
    ...


def is_point_inside_projection(
    ptest: PointType,
    v: VectorType,
    pts: PointType,
    tri: IndexType,
    fwd_only: bool = True,
) -> bool:
    ...
