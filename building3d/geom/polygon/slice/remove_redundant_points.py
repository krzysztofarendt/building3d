import numpy as np
from numba import njit

from building3d.geom.points import is_point_in_array
from building3d.geom.points import roll_forward
from building3d.geom.polygon.edges import polygon_edges
from building3d.geom.polygon.slice.locate_slicing_points import \
    locate_slicing_points
from building3d.geom.types import FLOAT
from building3d.geom.types import IndexType
from building3d.geom.types import PointType

from .constants import EDGE
from .constants import EXTERIOR
from .constants import INTERIOR
from .constants import INVALID_INDEX
from .constants import INVALID_LOC
from .constants import VERTEX


@njit
def remove_redundant_points(
    slicing_pts: PointType,
    pts: PointType,
    tri: IndexType,
    num_try: int = 0,
) -> PointType:
    """Keeps only these slicing points that are needed to perform the slice.

    Removes:
    - points outside the polygon
    - points touching the polygon vertices or edges except those needed to define the slice

    This function is useful if the slicing points come from another polygon.
    The second polygon might be overlapping with this one, so some of its vertices
    will be outside this polygon. Similarly, some edges might be overlapping.
    We need to keep only the points that create a polygonal chain slicing this polygon
    into two parts.

    Args:
        slicing_pts: points defining how to slice the polygon
        pts: polygon points
        tri: polygon triangles

    Return:
        slicing points with redundant points removed (can be empty)
    """
    assert len(pts.shape) == 2 and pts.shape[1] == 3
    assert len(slicing_pts.shape) == 2 and slicing_pts.shape[1] == 3

    edges = polygon_edges(pts)
    sploc = locate_slicing_points(slicing_pts, pts, tri, edges)

    if sploc[0][0] == INTERIOR or sploc[-1][0] == INTERIOR:
        if num_try > len(slicing_pts):
            return slicing_pts[0:1]  # Return empty list
        else:
            return remove_redundant_points(
                roll_forward(slicing_pts), pts, tri, num_try + 1
            )

    num_interior = sum([1 for loc, _ in sploc if loc == INTERIOR])
    num_at_vertex = sum([1 for loc, _ in sploc if loc == VERTEX])
    num_at_edge = sum([1 for loc, _ in sploc if loc == EDGE])

    # Special cases
    if len(slicing_pts) == 4 and len(pts) == 4:
        if num_at_vertex == 2 and num_at_edge == 2:
            # This is the only case that does not work with the remaining code,
            # so I need to detect it early and return :/
            # Let's keep only the edge points
            new_points = []
            for i in range(len(slicing_pts)):
                this_pt = slicing_pts[i]
                this_loc_type, this_loc_ix = sploc[i]

                if this_loc_type == EDGE:
                    new_points.append(this_pt)

            # Convert list of points to an array
            # (done this way to keep it compatible with numba)
            new_pts_arr = np.zeros((len(new_points), 3), dtype=FLOAT)
            for i in range(len(new_points)):
                new_pts_arr[i] = new_points[i]

            return new_pts_arr


    # Standard cases
    new_points = []
    for i in range(len(slicing_pts)):
        # Collect information:
        # - point
        # - location type
        # - location index
        # for:
        # - previous point
        # - this point
        # - next point

        # This point
        this_pt = slicing_pts[i]
        this_loc_type, this_loc_ix = sploc[i]

        # Previous point
        if i > 0:
            prev_loc_type, prev_loc_ix = sploc[i - 1]
        else:
            prev_loc_type = INVALID_LOC
            prev_loc_ix = INVALID_INDEX

        # Next point
        if i < len(slicing_pts) - 1:
            next_loc_type, next_loc_ix = sploc[i + 1]
        else:
            next_loc_type = INVALID_LOC
            next_loc_ix = INVALID_INDEX

        # Check if this point should be kept or removed
        if this_loc_type == EXTERIOR:
            # Points outside polygon are not included
            continue

        elif this_loc_type == INTERIOR:
            # Points inside the polygon are included
            new_points.append(this_pt)

        elif next_loc_type == INTERIOR and this_loc_type in (VERTEX, EDGE):
            # Points thouching a vertex or edge are included if the next one is inside the polygon
            new_points.append(this_pt)

        elif prev_loc_type == INTERIOR and this_loc_type in (VERTEX, EDGE):
            # This is the last needed point
            new_points.append(this_pt)
            break

        elif this_loc_type == VERTEX and next_loc_type == VERTEX and prev_loc_type != EDGE:
            if num_interior == 0 and this_loc_ix != next_loc_ix:
                # Include it, because there are no interior points
                # and it is a slice from vertex to vertex
                new_points.append(this_pt)
            else:
                # Don't include it, because it is not crossing the polygon
                # (the segment from this to next point is along the edge)
                continue

        elif this_loc_type == VERTEX and prev_loc_type == VERTEX and next_loc_type != EDGE:
            if num_interior == 0 and this_loc_ix != prev_loc_ix:
                # Include it, because there are no interior points
                # and it is a slice from vertex to vertex
                # (same case as the previous one, but the other end of the slice)
                new_points.append(this_pt)
            else:
                # Don't include it, because it is not crossing the polygon
                # (the segment from this to next point is along the edge)
                continue

        elif this_loc_type == EDGE and next_loc_type == EDGE:
            if num_interior == 0 and this_loc_ix != next_loc_ix:
                # Include it, because there are no interior points
                # and it is a slice from edge to edge
                new_points.append(this_pt)
            else:
                # Don't include it, because it is not crossing the polygon
                # (the segment from this to next point is along the edge)
                continue

        elif this_loc_type == EDGE and prev_loc_type == EDGE:
            if num_interior == 0 and this_loc_ix != prev_loc_ix:
                # Include it, because there are no interior points
                # and it is a slice from edge to edge
                # (same case as the previous one, but the other end of the slice)
                new_points.append(this_pt)
                # This is the last needed point
                break
            else:
                # Don't include it, because it is not crossing the polygon
                # (the segment from this to next point is along the edge)
                continue

        elif this_loc_type == VERTEX and next_loc_type == EDGE:
            if num_interior == 0 and not is_point_in_array(this_pt, edges[next_loc_ix]):
                new_points.append(this_pt)
            else:
                continue

        elif this_loc_type == VERTEX and prev_loc_type == EDGE:
            if num_interior == 0 and not is_point_in_array(this_pt, edges[prev_loc_ix]):
                new_points.append(this_pt)
            else:
                continue

        elif this_loc_type == EDGE and next_loc_type == VERTEX:
            if num_interior == 0 and not is_point_in_array(
                pts[next_loc_ix], edges[this_loc_ix]
            ):
                new_points.append(this_pt)
            else:
                continue

        elif this_loc_type == EDGE and prev_loc_type == VERTEX:
            if num_interior == 0 and not is_point_in_array(
                pts[prev_loc_ix], edges[this_loc_ix]
            ):
                new_points.append(this_pt)
            else:
                continue

    # Convert list of points to an array
    # (done this way to keep it compatible with numba)
    new_pts_arr = np.zeros((len(new_points), 3), dtype=FLOAT)
    for i in range(len(new_points)):
        new_pts_arr[i] = new_points[i]

    return new_pts_arr
