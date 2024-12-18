import numpy as np
from numba import njit

from building3d.geom.points.distance import distance_point_to_edge
from building3d.geom.polygon.edges import polygon_edges
from building3d.geom.polygon.ispointinside import \
    is_point_inside_ortho_projection
from building3d.geom.polygon.plane import plane_coefficients
from building3d.geom.polygon.plane import projection_coefficients
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.types import VectorType

@njit
def distance_point_to_polygon(
    ptest: PointType,
    pts: PointType,
    tri: IndexType,
    vn: VectorType,
) -> float:
    """Return distance of point to the polygon.

    Note:
        For points not laying inside the orthogonal
        projection, the distance is calculated as the distance
        to the closest edge.

    Args:
        ptest: tested point, shape (3, )
        pts: polygon's points, shape (num_pts, 3)
        tri: polygon's triangles, shape (num_tri, 3)
        vn: polygon's normal vector, shape (3, )

    Return:
        scalar distance
    """
    # Translate polygon's to the point p
    _, _, _, d = plane_coefficients(pts)
    _, _, _, dp = projection_coefficients(ptest, vn)

    # Distance (sign neglected!)
    # Negative distance -> point behind the polygon
    # Positive distance -> point in front of the polygon
    dist = (np.dot(vn, ptest) + d) / np.linalg.norm(vn)

    if is_point_inside_ortho_projection(ptest, pts, tri):
        return np.abs(dist)
    else:
        # Return distance to the closest edge
        min_dist = np.inf
        for ed in polygon_edges(pts):
            edge_dist = distance_point_to_edge(ptest, ed[0], ed[1])
            if edge_dist < min_dist:
                min_dist = edge_dist
        return float(min_dist)
