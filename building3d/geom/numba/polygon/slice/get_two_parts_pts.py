from numba import njit
import numpy as np

from building3d.geom.numba.points import points_equal, is_point_in_array, list_pts_to_array
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.exceptions import GeometryError
from building3d.geom.numba.vectors import normal
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.polygon.slice.remove_redundant_points import remove_redundant_points
from building3d.geom.numba.polygon.slice.locate_slicing_points import locate_slicing_points
from .constants import EXTERIOR, INTERIOR, VERTEX, EDGE, INVALID_INDEX


@njit
def get_two_parts_pts(
    pts: PointType,
    tri: IndexType,
    slicing_pts: PointType,
):
    """Slices a polygon into two parts.

    Slicing rules:
    - the first and the last slicing point must be touching a vertex or an edge
    - if more is touching vertex/edge at the beginning of the list, they are removed
      so that the list starts with a single vertex/edge touching point
    - the same applies to the end of the slicing points list

    Possible cases:
    1) slicing points start and end at two different edges
    2) slicing points start and end at the same edge
    3) slicing points start at a vertex and end at some edge (or vice versa)
    4) Slicing points start and end at two different vertices

    Args:
        pts: polygon points
        tri: polygon triangles
        slicing_pts: slicing points
        name1: name of the first part of the sliced polygon
        pt1: some reference point used to identify the first part of the slice
        name2: name of the second part of the sliced polygon
        pt2: some reference point used to identify the second part of the slice

    Return:
        (pts1, pts2)
    """
    # Make sure there is enough slicing points (at least 2)
    if slicing_pts.shape[0] < 2:
        raise GeometryError("Cannot slice the polygon using less than 2 points")

    # Make sure all slicing points are within this polygon
    for pt in slicing_pts:
        if not is_point_inside(pt, pts, tri):
            raise GeometryError("At least one of the points is not inside the polygon")

    # Get the edges of the polygon
    poly_edges = polygon_edges(pts)

    # Clean slicing points: remove heading or trailing vertex/edge points
    slicing_pts = remove_redundant_points(slicing_pts, pts, tri, poly_edges)
    if slicing_pts.shape[0] < 2:
        raise GeometryError("Cannot slice the polygon using less than 2 points")

    # Find out which case is it
    poly_edges = polygon_edges(pts)
    sploc = locate_slicing_points(slicing_pts, pts, tri, poly_edges)
    num_at_vertex = sum([1 for loc, _ in sploc if loc == VERTEX])
    num_at_edge = sum([1 for loc, _ in sploc if loc == EDGE])
    num_interior = sum([1 for loc, _ in sploc if loc == INTERIOR])
    sl_edges = set([index for loc, index in sploc if loc == EDGE])
    sl_vertices = set([index for loc, index in sploc if loc == VERTEX])

    assert num_at_vertex + num_at_edge + num_interior == len(slicing_pts), \
        "Slicing point location counting must have a bug"

    case = None
    if num_at_edge == 2 and len(sl_edges) == 2 and num_at_vertex == 0:
        # 1) slicing points start and end at two different edges
        case = 1
    elif num_at_edge == 2 and len(sl_edges) == 1 and num_at_vertex == 0:
        # 2) slicing points start and end at the same edge
        case = 2
    elif num_at_edge == 1 and num_at_vertex == 1:
        # 3) slicing points start at a vertex and end at some edge (or vice versa)
        case = 3
    elif num_at_vertex == 2 and len(sl_vertices) == 2 and num_at_edge == 0:
        # 4) Slicing points start and end at two different vertices
        case = 4
    else:
        raise NotImplementedError("Case not implemented? Debugging needed.")

    # Create two polygons through slicing
    if case == 1:
        # 1) slicing points start and end at two different edges
        assert sploc[0][0] == EDGE
        assert sploc[len(slicing_pts) - 1][0] == EDGE
        edge_num_1 = sploc[0][1]
        edge_num_2 = sploc[len(slicing_pts) - 1][1]

        # Polygon 1 and Polygon 2
        points_1 = []
        points_1.extend(slicing_pts)
        points_2 = []
        points_2.extend(slicing_pts)

        next_1 = 0
        next_2 = 0
        last_1 = 0
        last_2 = 0

        for i in range(len(pts)):
            if points_equal(pts[i], poly_edges[edge_num_2, 0]):
                next_1 = i
            if points_equal(pts[i], poly_edges[edge_num_2, 1]):
                next_2 = i
            if points_equal(pts[i], poly_edges[edge_num_1][1]):
                last_1 = i
            if points_equal(pts[i], poly_edges[edge_num_1][0]):
                last_2 = i

        if next_1 < next_2 or next_2 == 0:
            inc_1 = -1
        else:
            inc_1 = -1

        inc_2 = inc_1 * -1  # Polygon 2 goes the other way around

        while next_1 != last_1:
            points_1.append(pts[next_1])
            next_1 += inc_1
            if next_1 < 0:
                next_1 = len(pts) - 1
            elif next_1 > len(pts) - 1:
                next_1 = 0
        points_1.append(pts[next_1])

        while next_2 != last_2:
            points_2.append(pts[next_2])
            next_2 += inc_2
            if next_2 < 0:
                next_2 = len(pts) - 1
            elif next_2 > len(pts) - 1:
                next_2 = 0
        points_2.append(pts[next_2])

        pts1 = list_pts_to_array(points_1)
        pts2 = list_pts_to_array(points_2)

    elif case == 2:
        # 2) slicing points start and end at the same edge
        edge_num = sl_edges.pop()

        # Polygon 1 is composed of slice_points only
        # poly_1 = Polygon(points, name=name1)
        pts1 = slicing_pts.copy()  # name=name1

        # Polygon 2 is composed of both, own points and sliced points
        # slicing_pts must have opposite order than pts -> compare their normal vectors
        slicing_vn = normal(slicing_pts[-1], slicing_pts[0], slicing_pts[1])
        poly_vn = normal(pts[-1], pts[0], pts[1])
        if np.allclose(-1 * slicing_vn, poly_vn):
            pass
        elif np.allclose(slicing_vn, poly_vn):
            slicing_pts = slicing_pts[::-1]  # Re-ordering needed
        else:
            raise ValueError("Unexpected slicing plane orientation")

        points_2 = []
        slice_points_included = False
        for p in pts:
            points_2.append(p)
            if is_point_in_array(p, poly_edges[edge_num]):
                # Slicing ocurred at this edge - need to add slice_points
                if not slice_points_included:
                    for sp in slicing_pts:
                        points_2.append(sp)
                    slice_points_included = True

        pts2 = list_pts_to_array(points_2)

    elif case == 3:
        # 3) slicing points start at a vertex and end at some edge (or vice versa)
        edge_num = sl_edges.pop()
        assert len(sl_edges) == 0, "Should be no edges left in this case"

        # Determine if first point starts at vertex or the last point ends at vertex
        if sploc[0][0] == VERTEX:
            start_at_vertex = True
            assert sploc[len(slicing_pts) - 1][0] == EDGE
        else:
            start_at_vertex = False
            assert sploc[len(slicing_pts) - 1][0] == VERTEX

        points_1 = []
        points_2 = []
        if start_at_vertex:
            points_1.extend(slicing_pts)
            points_2.extend(slicing_pts)
        else:
            points_1.extend(slicing_pts[::-1])
            points_2.extend(slicing_pts[::-1])

        next_1 = 0
        next_2 = 0
        last_1 = 0
        last_2 = 0

        for i in range(len(pts)):
            if points_equal(pts[i], poly_edges[edge_num, 0]):
                next_1 = i
            if points_equal(pts[i], poly_edges[edge_num, 1]):
                next_2 = i
            if points_equal(pts[i], points_1[0]):
                last_1 = i
            if points_equal(pts[i], points_2[0]):
                last_2 = i

        assert last_1 == last_2, "They should both end up at the same vertex"

        if next_1 < next_2 or next_2 == 0:
            inc_1 = -1
        else:
            inc_1 = -1

        inc_2 = inc_1 * -1  # Polygon 2 goes the other way around

        while next_1 != last_1:
            points_1.append(pts[next_1])
            next_1 += inc_1
            if next_1 < 0:
                next_1 = len(pts) - 1
            elif next_1 > len(pts) - 1:
                next_1 = 0

        while next_2 != last_2:
            points_2.append(pts[next_2])
            next_2 += inc_2
            if next_2 < 0:
                next_2 = len(pts) - 1
            elif next_2 > len(pts) - 1:
                next_2 = 0

        pts1 = list_pts_to_array(points_1)
        pts2 = list_pts_to_array(points_2)

    elif case == 4:
        # 4) Slicing points start and end at two different vertices
        # Polygon 1
        pi_start = 0
        pi_end = 0
        for i in range(len(pts)):
            if points_equal(pts[i], slicing_pts[0]):
                pi_start = i
            if points_equal(pts[i], slicing_pts[-1]):
                pi_end = i

        points_1 = []
        current = pi_start
        last = pi_end
        while current != last:
            points_1.append(pts[current])
            current += 1
            if current > len(pts) - 1:
                current = 0

        for i in range(len(slicing_pts) - 1, 0, -1):
            points_1.append(slicing_pts[i])

        # Polygon 2 must go the other way around ####
        points_2 = []                               #
        current = pi_start                          #
        last = pi_end                               #
        while current != last:                      #
            points_2.append(pts[current])   #
            current -= 1 # <------------------------#
            if current < 0:
                current = len(pts) - 1

        for i in range(len(slicing_pts) - 1, 0, -1):
            points_2.append(slicing_pts[i])

        pts1 = list_pts_to_array(points_1)
        pts2 = list_pts_to_array(points_2)

    else:
        raise NotImplementedError("Case not implemented yet")

    return (pts1, pts2)
