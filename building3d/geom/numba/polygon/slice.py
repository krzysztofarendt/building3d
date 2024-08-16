from numba import njit
import numpy as np

from building3d import random_id
from building3d.geom.numba.points import points_equal
from building3d.geom.numba.types import PointType, IndexType, FLOAT, INT
from building3d.geom.exceptions import GeometryError
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.distance import distance_point_to_edge


# @njit
# def slice(
#     pts: PointType,
#     tri: IndexType,
#     name1: str | None = None,
#     pt1: PointType | None = None,
#     name2: str | None = None,
#     pt2: PointType | None = None,
# ):
#     """Slice a polygon into two parts.
#
#     If `name1` and `name2` are given, at least one `pt1` or `pt2` must be provided.
#
#     Slicing rules:
#     - the first and the last slicing point must be touching a vertex or an edge
#     - if more is touching vertex/edge at the beginning of the list, they are removed
#       so that the list starts with a single vertex/edge touching point
#     - the same applies to the end of the slicing points list
#
#     Possible cases:
#     1) slicing points start and end at two different edges
#     2) slicing points start and end at the same edge
#     3) slicing points start at a vertex and end at some edge (or vice versa)
#     4) Slicing points start and end at two different vertices
#
#     Args:
#         points: list of points
#         name1: name of the first part
#         pt1: some point used to identify the first part
#         name2: name of the second part
#         pt2: some point used to identify the second part
#
#     Return:
#         (pts1, pts2)
#     """
#     # Make sure there is enough slicing points (at least 2)
#     if pts.shape[0] < 2:
#         raise GeometryError("Cannot slice the polygon using less than 2 points")
#
#     # Make sure all slicing points are within this polygon
#     for p in pts:
#         if not is_point_inside(p, pts, tri):
#             raise GeometryError("At least one of the points is not inside the polygon")
#
#     if name1 is None:
#         name1 = random_id()
#     if name2 is None:
#         name2 = random_id()
#
#
# @njit
# def remove_trailing_boundary_touching_points(
#     pts: PointType,
#     slicing_pts: PointType,
# ) -> PointType:
#     """Remove all heading and trailing slicing points touching a vertex or an edge.
#
#     The returned list of points starts with a single vertex touching polygon's
#     vertex or edge and ends with a single vertex touching an edge or a vertex.
#     """
#     sl_pt_loc = self._slicing_point_location(slicing_pts)
#     num_at_vertex = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_vertex"])
#     num_at_edge = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_edge"])
#     num_interior = sum([1 for loc, _ in sl_pt_loc.values() if loc == "interior"])
#
#     new_points = []
#     for i in range(len(slicing_pts)):
#         # Collect point, location type, and location index for previous, this, and next point
#         this_pt = slicing_pts[i]
#         this_loc_type, this_loc_ix = sl_pt_loc[i]
#
#         if i > 0:
#             prev_loc_type, prev_loc_ix = sl_pt_loc[i - 1]
#         else:
#             prev_loc_type = None
#             prev_loc_ix = None
#
#         if i < len(slicing_pts) - 1:
#             next_pt = slicing_pts[i + 1]
#             next_loc_type, next_loc_ix = sl_pt_loc[i + 1]
#         else:
#             next_pt = None
#             next_loc_type = None
#             next_loc_ix = None
#
#         neglect_subsequent = False
#
#         # Check if this point should be kept or removed
#         if neglect_subsequent is True:
#             continue
#         elif this_loc_type == "interior":
#             new_points.append(this_pt)
#         elif next_loc_type == "interior":
#             new_points.append(this_pt)
#         elif (
#             prev_loc_type is not None
#             and prev_loc_type == "interior"
#             and this_loc_type in ("at_vertex", "at_edge")
#         ):
#             new_points.append(this_pt)
#             neglect_subsequent = True
#         elif this_loc_type == "at_vertex" and next_loc_type == "at_vertex":
#             if num_at_vertex == 2:
#                 # It means there are no interior points
#                 assert num_interior == 0
#                 new_points.append(this_pt)
#             else:
#                 continue
#         elif this_loc_type == "at_vertex" and prev_loc_type == "at_vertex":
#             if num_at_vertex == 2:
#                 # It means there are no interior points
#                 assert num_interior == 0
#                 new_points.append(this_pt)
#             else:
#                 continue
#         elif this_loc_type == "at_edge" and next_loc_type == "at_edge":
#             if this_loc_ix != next_loc_ix:
#                 # It means there are no interior points
#                 assert num_interior == 0
#                 new_points.append(this_pt)
#             else:
#                 continue
#         elif (
#             this_loc_type == "at_edge"
#             and next_loc_type is None
#             and prev_loc_type == "at_edge"
#             and prev_loc_ix is not None
#             and prev_loc_ix != this_loc_ix
#         ):
#             # It means there are no interior points
#             # and this is the last slicing point
#             assert num_interior == 0
#             new_points.append(this_pt)
#         elif (
#             this_loc_type == "at_edge"
#             and next_loc_type is None
#             and prev_loc_type == "at_edge"
#             and prev_loc_ix is not None
#             and prev_loc_ix == this_loc_ix
#         ):
#             # It means there must be some interior points
#             # and this is the last slicing point
#             # and this and previous points lay on the same edge
#             # so this one must be removed
#             assert num_interior > 0
#             continue
#         elif (
#             this_loc_type in ("at_vertex", "at_edge")
#             and next_loc_type != "interior"
#         ):
#             continue
#         elif (
#             this_loc_type == "at_vertex"
#             and next_loc_type == "at_edge"
#             and next_loc_ix is not None
#         ):
#             d = distance_point_to_edge(
#                 ptest = this_pt,
#                 p1 = self.edges[next_loc_ix][0],
#                 p2 = self.edges[next_loc_ix][1],
#             )
#             if np.isclose(d, 0):
#                 continue
#             else:
#                 new_points.append(this_pt)
#         elif (
#             this_loc_type == "at_edge"
#             and next_loc_type == "at_vertex"
#             and next_pt is not None
#         ):
#             d = distance_point_to_edge(
#                 ptest = next_pt,
#                 p1 = self.edges[this_loc_ix][0],
#                 p2 = self.edges[this_loc_ix][1],
#             )
#             if np.isclose(d, 0):
#                 continue
#             else:
#                 new_points.append(this_pt)
#         else:
#             raise RuntimeError("This should never happen. Some case is not considered (bug!).")
#
#     return new_points


@njit
def slicing_point_location(pts: PointType, slicing_pts: PointType) -> dict:
    """Return the location of each slicing point.

    The returned dict has the following format:
    `{slicing_point_index: (location_string, location_index)}`.
    `location_index` is either vertex index, edge index, or `-1` (for `interior`).
    `location_string` is `at_vertex`, `at_edge`, or `interior`.
    """
    if len(slicing_pts) == 0:
        raise GeometryError("No slicing points passed")

    poly_edges = polygon_edges(pts)

    sl_pt_loc = {}
    for slp_i, slp in enumerate(slicing_pts):
        for p_i, p in enumerate(pts):
            if points_equal(p, slp):
                sl_pt_loc[slp_i] = ("at_vertex", p_i)
                break

        if slp_i in sl_pt_loc:
            continue

        for edge_num, (ep1, ep2) in enumerate(poly_edges):
            d_to_edge = distance_point_to_edge(ptest=slp, pt1=ep1, pt2=ep2)
            if np.isclose(d_to_edge, 0):
                sl_pt_loc[slp_i] = ("at_edge", edge_num)

        if slp_i in sl_pt_loc:
            continue
        else:
            sl_pt_loc[slp_i] = ("interior", -1)

    if sl_pt_loc[0][0] == "interior":
        raise GeometryError("First slicing point must start at an edge or a vertex")
    if sl_pt_loc[len(slicing_pts) - 1][0] == "interior":
        raise GeometryError("Last slicing point must end at an edge or a vertex")

    return sl_pt_loc
