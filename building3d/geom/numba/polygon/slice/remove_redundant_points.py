from numba import njit
import numpy as np

from building3d.geom.numba.types import PointType, IndexType, FLOAT
from building3d.geom.numba.polygon.distance import distance_point_to_edge
from building3d.geom.numba.polygon.slice.locate_slicing_points import locate_slicing_points
from .constants import INTERIOR, VERTEX, EDGE, INVALID_INDEX, INVALID_LOC, INVALID_PT


@njit
def remove_redundant_points(
    slicing_pts: PointType,
    pts: PointType,
    tri: IndexType,
    poly_edges: PointType,
) -> PointType:
    """Removes all heading and trailing slicing points touching a vertex or an edge.

    The returned list of points starts with a single vertex touching polygon's
    vertex or edge and ends with a single vertex touching an edge or a vertex.

    This function is useful if the slicing points come from another polygon.
    The second polygon might be overlapping with this one, so some of its vertices
    will be outside this polygon. Similarly, some edges might be overlapping.
    We need to keep only the points that create a polygonal chain slicing this polygon
    into two parts.

    Args:
        pts: polygon points
        slicing_pts: points defining how to slice the polygon
        poly_edges: polygon edges

    Return:
        slicing points with redundant points removed
    """
    assert len(pts.shape) == 2 and pts.shape[1] == 3
    assert len(slicing_pts.shape) == 2 and slicing_pts.shape[1] == 3
    print("DEBUG")
    sploc = locate_slicing_points(slicing_pts, pts, tri, poly_edges)

    num_at_vertex = sum([1 for loc, _ in sploc if loc == VERTEX])
    num_interior = sum([1 for loc, _ in sploc if loc == INTERIOR])

    new_points = []
    for i in range(len(slicing_pts)):
        # Collect point, location type, and location index for previous, this, and next point
        this_pt = slicing_pts[i]
        this_loc_type, this_loc_ix = sploc[i]

        if i > 0:
            prev_loc_type, prev_loc_ix = sploc[i - 1]
        else:
            prev_loc_type = INVALID_LOC
            prev_loc_ix = INVALID_INDEX

        if i < len(slicing_pts) - 1:
            next_pt = slicing_pts[i + 1]
            next_loc_type, next_loc_ix = sploc[i + 1]
        else:
            next_pt = INVALID_PT
            next_loc_type = INVALID_LOC
            next_loc_ix = INVALID_INDEX

        neglect_subsequent = False

        # Check if this point should be kept or removed
        if neglect_subsequent is True:
            continue
        elif this_loc_type == INTERIOR:
            new_points.append(this_pt)
        elif next_loc_type == INTERIOR:
            new_points.append(this_pt)
        elif (
            prev_loc_type != INVALID_LOC
            and prev_loc_type == INTERIOR
            and this_loc_type in (VERTEX, EDGE)
        ):
            new_points.append(this_pt)
            neglect_subsequent = True
        elif this_loc_type == VERTEX and next_loc_type == VERTEX:
            if num_at_vertex == 2:
                # It means there are no interior points
                assert num_interior == 0
                new_points.append(this_pt)
            else:
                continue
        elif this_loc_type == VERTEX and prev_loc_type == VERTEX:
            if num_at_vertex == 2:
                # It means there are no interior points
                assert num_interior == 0
                new_points.append(this_pt)
            else:
                continue
        elif this_loc_type == EDGE and next_loc_type == EDGE:
            if this_loc_ix != next_loc_ix:
                # It means there are no interior points
                assert num_interior == 0
                new_points.append(this_pt)
            else:
                continue
        elif (
            this_loc_type == EDGE
            and next_loc_type == INVALID_LOC
            and prev_loc_type == EDGE
            and prev_loc_ix >= 0
            and prev_loc_ix != this_loc_ix
        ):
            # It means there are no interior points
            # and this is the last slicing point
            assert num_interior == 0
            new_points.append(this_pt)
        elif (
            this_loc_type == EDGE
            and next_loc_type == INVALID_LOC
            and prev_loc_type == EDGE
            and prev_loc_ix >= 0
            and prev_loc_ix == this_loc_ix
        ):
            # It means there must be some interior points
            # and this is the last slicing point
            # and this and previous points lay on the same edge
            # so this one must be removed
            assert num_interior > 0
            continue
        elif (
            this_loc_type in (VERTEX, EDGE)
            and next_loc_type != INTERIOR
        ):
            continue
        elif (
            this_loc_type == VERTEX
            and next_loc_type == EDGE
            and next_loc_ix >= 0
        ):
            edge = poly_edges[next_loc_ix]
            d = distance_point_to_edge(  # TODO: This is already calculated in sploc
                ptest = this_pt,
                pt1 = edge[0],
                pt2 = edge[1],
            )
            if np.isclose(d, 0):
                continue
            else:
                new_points.append(this_pt)
        elif (
            this_loc_type == EDGE
            and next_loc_type == VERTEX
            and next_pt is not INVALID_PT
        ):
            edge = poly_edges[this_loc_ix]
            d = distance_point_to_edge(  # TODO: This is already calculated in sploc
                ptest = next_pt,
                pt1 = edge[0],
                pt2 = edge[1],
            )
            if np.isclose(d, 0):
                continue
            else:
                new_points.append(this_pt)
        else:
            raise RuntimeError("This should never happen. Some case is not considered (bug!).")

    # Convert list of points to an array
    # (done this way to keep it compatible with numba)
    new_pts_arr = np.zeros((len(new_points), 3), dtype=FLOAT)
    for i in range(len(new_points)):
        new_pts_arr[i] = new_points[i]

    return new_pts_arr
