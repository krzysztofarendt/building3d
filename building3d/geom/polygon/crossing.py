import numpy as np
from numba import njit

from building3d.geom.points import are_points_coplanar
from building3d.geom.bboxes import bounding_box
from building3d.geom.points import new_point_between_2_points
from building3d.geom.points import points_equal
from building3d.geom.points.distance import distance_point_to_edge
from building3d.geom.points.intersections import line_segment_intersection
from building3d.geom.polygon.edges import polygon_edges
from building3d.geom.polygon.ispointinside import is_point_inside
from building3d.geom.polygon.plane import plane_coefficients
from building3d.geom.types import FLOAT
from building3d.geom.types import IndexType
from building3d.geom.types import PointType


@njit
def are_polygons_crossing(
    pts1: PointType,
    tri1: IndexType,
    pts2: PointType,
    tri2: IndexType,
) -> bool:
    """Checks if two polygons are crossing (overlapping to some extent)."""
    bbox1 = bounding_box(pts1)
    bbox2 = bounding_box(pts2)
    if not are_bboxes_overlapping(bbox1, bbox2):
        return False

    if not are_points_coplanar(np.vstack((pts1, pts2))):
        return False

    for e1 in polygon_edges(pts1):
        for e2 in polygon_edges(pts2):
            if (
                points_equal(e1[0], e2[0])
                or points_equal(e1[0], e2[1])
                or points_equal(e1[1], e2[1])
                or points_equal(e1[1], e2[0])
            ):
                continue
            else:
                p_cross = line_segment_intersection(e1[0], e1[1], e2[0], e2[1])
                if np.isnan(p_cross).any():
                    continue
                elif np.isclose(
                    distance_point_to_edge(p_cross, e1[0], e1[1]), 0
                ) or np.isclose(distance_point_to_edge(p_cross, e2[0], e2[1]), 0):
                    for x in np.linspace(0, 1, 10):
                        p_mid = new_point_between_2_points(e1[0], e1[1], rel_d=x)
                        if is_point_inside(p_mid, pts2, tri2, boundary_in=False):
                            return True
                        p_mid = new_point_between_2_points(e2[0], e2[1], rel_d=x)
                        if is_point_inside(p_mid, pts1, tri1, boundary_in=False):
                            return True
                else:
                    return True
    return False


@njit
def are_bboxes_overlapping(bbox1, bbox2):
    if (bbox1[1] < bbox2[0]).any() or (bbox1[0] > bbox2[1]).any():
        return False
    else:
        return True


@njit
def is_line_segment_crossing_polygon(
    seg_start: PointType,
    seg_end: PointType,
    pts: PointType,
    tri: IndexType,
    epsilon: float = 1e-10,
) -> bool:
    """
    Check if a line segment crosses a polygon in 3D space.

    Args:
        seg_start: Start point of the line segment (shape: (3,))
        seg_end: End point of the line segment (shape: (3,))
        pts: Array of polygon vertices (shape: (n, 3) where n is the number of vertices)
        tri: Array of polygon faces (shape: (f, 3) where f is the number of faces)
        epsilon: Small value for floating-point comparisons

    Returns:
        bool: True if the line segment crosses the polygon, False otherwise
    """
    # Get the plane equation coefficients
    a, b, c, d = plane_coefficients(pts)
    plane_normal = np.array([a, b, c])

    # Check if the line segment is parallel to the polygon's plane
    segment_direction = (seg_end - seg_start).astype(FLOAT)
    if abs(np.dot(segment_direction, plane_normal)) < epsilon:
        return False

    # Calculate the intersection point of the line with the plane
    t = -(a * seg_start[0] + b * seg_start[1] + c * seg_start[2] + d) / np.dot(
        segment_direction, plane_normal
    )

    # Check if the intersection point is within the line segment
    if t < 0 or t > 1:
        return False

    intersect_pt = seg_start + t * segment_direction

    # Check if the intersection point is inside the polygon
    return is_point_inside(intersect_pt, pts, tri, boundary_in=True)
