from numba import njit
import numpy as np

from building3d.geom.numba.points.distance import distance_point_to_edge
from building3d.geom.numba.points.intersections import line_segment_intersection
from building3d.geom.numba.points import new_point_between_2_points
from building3d.geom.numba.points import points_equal
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.numba.points import bounding_box


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
