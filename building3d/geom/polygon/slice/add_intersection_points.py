from numba import njit, typed, types
import numpy as np

from building3d.geom.types import PointType
from building3d.geom.points import points_equal
from building3d.geom.points import list_pts_to_array
from building3d.geom.points.intersections import line_segment_intersection
from building3d.geom.polygon.edges import polygon_edges
from .constants import INVALID_INDEX


@njit
def add_intersection_points(
    pts1: PointType, pts2: PointType
) -> tuple[PointType, PointType]:
    """Adds new points to `pts1` and `pts2` where edges of both point lists intersect."""
    edges1 = polygon_edges(pts1)
    edges2 = polygon_edges(pts2)

    out1 = []
    out2 = []

    # Find intersection points
    intersect_pts = []  # List of intersection points
    intersect_ix1 = {}  # Mapping from edge index (edges1) to intersection point index
    intersect_ix2 = {}  # Mapping from edge index (edges2) to intersection point index
    pt_index = INVALID_INDEX

    for i1 in range(edges1.shape[0]):
        for i2 in range(edges2.shape[0]):
            pt = line_segment_intersection(
                pa1=edges1[i1, 0],
                pb1=edges1[i1, 1],
                pa2=edges2[i2, 0],
                pb2=edges2[i2, 1],
            )
            if np.isnan(pt).any():
                # Invalid point, segments are not crossing
                continue
            elif points_equal(edges1[i1, 0], pt):
                # Don't add if intersection point is at the same time on of the vertices
                continue
            elif points_equal(edges1[i1, 1], pt):
                # Don't add if intersection point is at the same time on of the vertices
                continue
            elif points_equal(edges2[i2, 0], pt):
                # Don't add if intersection point is at the same time on of the vertices
                continue
            elif points_equal(edges2[i2, 1], pt):
                # Don't add if intersection point is at the same time on of the vertices
                continue
            else:
                intersect_pts.append(pt)
                pt_index = len(intersect_pts) - 1

                if i1 not in intersect_ix1:
                    # Typed list needed, because numba was unable to infer the type
                    intersect_ix1[i1] = typed.List.empty_list(types.int64)
                intersect_ix1[i1].append(pt_index)

                if i2 not in intersect_ix2:
                    # Typed list needed, because numba was unable to infer the type
                    intersect_ix2[i2] = typed.List.empty_list(types.int64)
                intersect_ix2[i2].append(pt_index)

    # Add intersection points
    for i1 in range(edges1.shape[0]):
        out1.append(edges1[i1, 0])
        if i1 in intersect_ix1:
            for pt_index in intersect_ix1[i1]:
                out1.append(intersect_pts[pt_index])

    for i2 in range(edges2.shape[0]):
        out2.append(edges2[i2, 0])
        if i2 in intersect_ix2:
            for pt_index in intersect_ix2[i2]:
                out2.append(intersect_pts[pt_index])

    new_pts1 = list_pts_to_array(out1)
    new_pts2 = list_pts_to_array(out2)

    return new_pts1, new_pts2
