from numba import njit
import numpy as np

from building3d.config import GEOM_ATOL
from building3d.geom.numba.types import PointType, VectorType, IndexType, FLOAT
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.triangles import is_point_inside as is_point_inside_triangle
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.points import distance_point_to_edge
from building3d.geom.numba.polygon.plane import plane_coefficients
from building3d.geom.numba.polygon.plane import projection_coefficients
from building3d.geom.numba.vectors import normal


@njit
def is_point_inside(
    ptest: PointType,
    pts: PointType,
    tri: IndexType,
) -> bool:
    """Checks whether a point lies on the surface of the polygon.

    If the point lays on an edge or vertex, it is assumed it is inside.

    Args:
        ptest: test point, array shape (3, )
        pts: polygon points, array shape (num_points, 3)
        tri: triangle indices, array shape (num_triangles, 3)

    Returns:
        True if ptest is inside the polygon
    """
    pts_stacked = np.zeros((pts.shape[0] + 1, 3), dtype=FLOAT)
    pts_stacked[:-1] = pts
    pts_stacked[-1] = ptest

    if not are_points_coplanar(pts_stacked):
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


@njit
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
            d = distance_point_to_edge(ptest, edge[0], edge[1])
            if d < margin:
                return False
    return True


@njit
def is_point_inside_ortho_projection(
    ptest: PointType,
    pts: PointType,
    tri: IndexType,
) -> bool:
    """Checks whether an orthogonally projected point hits the surface.

    The point is projected orthogonally to the polygon's plane.
    If the projected point is inside the polygon, returns True.
    """
    # Translate polygon's to the point p
    a, b, c, d = plane_coefficients(pts)
    vn = normal(pts[-1], pts[0], pts[1])
    ap, bp, cp, dp = projection_coefficients(ptest, vn)

    assert np.isclose(a, ap), "If a and ap are not equal, d should be normalized"
    assert np.isclose(b, bp), "If b and bp are not equal, d should be normalized"
    assert np.isclose(c, cp), "If c and cp are not equal, d should be normalized"

    # Distance
    # Negative distance -> point behind the polygon
    # Positive distance -> point in front of the polygon
    dist = d - dp

    # Make a copy of the polygon and move it to the point p
    moved_pts = pts + dist * vn

    # Check if the point lays inside the polygon
    is_inside = is_point_inside(ptest, moved_pts, tri)

    return is_inside


@njit
def is_point_inside_projection(
    ptest: PointType,
    v: VectorType,
    pts: PointType,
    tri: IndexType,
    fwd_only: bool = True,
) -> bool:
    """Checks whether a projected point hits the surface.

    The point is projected along the vector vec.
    It is possible to consider both positive and negative directions of vec,
    or only the positive.

    Args:
        ptest: tested point
        v: projection vector
        pts: polygon points array, shape (num_pts, 3)
        tri: polygon triangulation array (num_tri, 3)
        fwd_only: if True, only the forward (positive) direction of vec is considered

    Returns:
        True if the projected point hits the surface
    """
    # Get coefficients of the plane equation
    a, b, c, d = plane_coefficients(pts)

    # Find the point projection along vec to the plane of the polygon
    denom = a * v[0] + b * v[1] + c * v[2]

    if np.abs(denom) < GEOM_ATOL:
        # Vector vec is colinear with the plane
        # The point lays inside this projection only if it is inside this polygon
        # logger.warning(f"Projection vector {vec} is colinear with the polygon {self.name}")
        return is_point_inside(ptest, pts, tri)
    else:
        # Projection crosses the surface of the plane
        s = (-d - a * ptest[0] - b * ptest[1] - c * ptest[2]) / (a * v[0] + b * v[1] + c * v[2])

        if fwd_only and s < 0:
            # The plane is in the other direction than the one pointed by vec
            return False

        ptest = ptest + s * v
        is_inside = is_point_inside(ptest, pts, tri)
        return is_inside
