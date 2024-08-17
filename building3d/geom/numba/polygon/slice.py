from numba import njit
import numpy as np

from building3d import random_id
from building3d.geom.numba.points import points_equal, is_point_in_array, list_pts_to_array
from building3d.geom.numba.types import PointType, IndexType, FLOAT
from building3d.geom.exceptions import GeometryError
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.distance import distance_point_to_edge
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.vectors import normal


def slice_polygon(
    poly: Polygon,
    slicing_pts: PointType,
    pt1: PointType | None = None,
    name1: str | None = None,
    pt2: PointType | None = None,
    name2: str | None = None,
) -> tuple[Polygon, Polygon]:
    """Slice polygon into two parts.

    To assign names, all optional arguments needs to be provided.

    Args:
        poly: polygon instrance
        slicing_pts: slicing points
        pt1: optional point inside one of the resulting slices
        name1: optional name of part associated with pt1
        pt2: optional point inside the other one of the resulting slices
        name2: optional name of part associated with pt2

    Return:
        tuple of new polygons
    """
    pts1, pts2 = get_two_parts_pts(poly.pts, poly.tri, slicing_pts)
    poly1, poly2 = get_polygons(pts1, pts2, pt1, name1, pt2, name2)

    return poly1, poly2


def get_polygons(
    pts1: PointType,
    pts2: PointType,
    pt1: PointType | None = None,
    name1: str | None = None,
    pt2: PointType | None = None,
    name2: str | None = None,
) -> tuple[Polygon, Polygon]:
    """Get polygons from `pts1` and `pts2` and assign names.

    To assign names, all optional arguments needs to be provided.

    Args:
        poly: polygon instrance
        slicing_pts: slicing points
        pt1: optional point inside one of the resulting slices
        name1: optional name of part associated with pt1
        pt2: optional point inside the other one of the resulting slices
        name2: optional name of part associated with pt2

    Return:
        tuple of new polygons
    """
    poly1 = Polygon(pts1)
    poly2 = Polygon(pts2)

    if (
        pt1 is not None and
        name1 is not None and
        pt2 is not None and
        name2 is not None
    ):
        if poly1.is_point_inside(pt1):
            poly1.name = name1
        elif poly1.is_point_inside(pt2):
            poly1.name = name2
        else:
            raise GeometryError("None of the points is inside polygon made of pts1")

        if poly2.is_point_inside(pt1):
            poly2.name = name1
        elif poly2.is_point_inside(pt2):
            poly2.name = name2
        else:
            raise GeometryError("None of the points is inside polygon made of pts2")

    return (poly1, poly2)


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
    slicing_pts = remove_redundant_points(pts, slicing_pts, poly_edges)
    if slicing_pts.shape[0] < 2:
        raise GeometryError("Cannot slice the polygon using less than 2 points")

    # Find out which case is it
    poly_edges = polygon_edges(pts)
    sl_pt_loc = slicing_point_location(pts, slicing_pts, poly_edges)
    num_at_vertex = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_vertex"])
    num_at_edge = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_edge"])
    num_interior = sum([1 for loc, _ in sl_pt_loc.values() if loc == "interior"])
    sl_edges = set([index for loc, index in sl_pt_loc.values() if loc == "at_edge"])
    sl_vertices = set([index for loc, index in sl_pt_loc.values() if loc == "at_vertex"])

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
        assert sl_pt_loc[0][0] == "at_edge"
        assert sl_pt_loc[len(slicing_pts) - 1][0] == "at_edge"
        edge_num_1 = sl_pt_loc[0][1]
        edge_num_2 = sl_pt_loc[len(slicing_pts) - 1][1]

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
        if sl_pt_loc[0][0] == "at_vertex":
            start_at_vertex = True
            assert sl_pt_loc[len(slicing_pts) - 1][0] == "at_edge"
        else:
            start_at_vertex = False
            assert sl_pt_loc[len(slicing_pts) - 1][0] == "at_vertex"

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


@njit
def remove_redundant_points(
    pts: PointType,
    slicing_pts: PointType,
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

    sl_pt_loc = slicing_point_location(pts, slicing_pts, poly_edges)

    num_at_vertex = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_vertex"])
    num_interior = sum([1 for loc, _ in sl_pt_loc.values() if loc == "interior"])

    new_points = []
    for i in range(len(slicing_pts)):
        # Collect point, location type, and location index for previous, this, and next point
        this_pt = slicing_pts[i]
        this_loc_type, this_loc_ix = sl_pt_loc[i]

        if i > 0:
            prev_loc_type, prev_loc_ix = sl_pt_loc[i - 1]
        else:
            prev_loc_type = None
            prev_loc_ix = -1  # None not accepted by numba, because it is later used as index

        if i < len(slicing_pts) - 1:
            next_pt = slicing_pts[i + 1]
            next_loc_type, next_loc_ix = sl_pt_loc[i + 1]
        else:
            next_pt = None
            next_loc_type = None
            next_loc_ix = -1  # None not accepted by numba, because it is later used as index

        neglect_subsequent = False

        # Check if this point should be kept or removed
        if neglect_subsequent is True:
            continue
        elif this_loc_type == "interior":
            new_points.append(this_pt)
        elif next_loc_type == "interior":
            new_points.append(this_pt)
        elif (
            prev_loc_type is not None
            and prev_loc_type == "interior"
            and this_loc_type in ("at_vertex", "at_edge")
        ):
            new_points.append(this_pt)
            neglect_subsequent = True
        elif this_loc_type == "at_vertex" and next_loc_type == "at_vertex":
            if num_at_vertex == 2:
                # It means there are no interior points
                assert num_interior == 0
                new_points.append(this_pt)
            else:
                continue
        elif this_loc_type == "at_vertex" and prev_loc_type == "at_vertex":
            if num_at_vertex == 2:
                # It means there are no interior points
                assert num_interior == 0
                new_points.append(this_pt)
            else:
                continue
        elif this_loc_type == "at_edge" and next_loc_type == "at_edge":
            if this_loc_ix != next_loc_ix:
                # It means there are no interior points
                assert num_interior == 0
                new_points.append(this_pt)
            else:
                continue
        elif (
            this_loc_type == "at_edge"
            and next_loc_type is None
            and prev_loc_type == "at_edge"
            and prev_loc_ix >= 0
            and prev_loc_ix != this_loc_ix
        ):
            # It means there are no interior points
            # and this is the last slicing point
            assert num_interior == 0
            new_points.append(this_pt)
        elif (
            this_loc_type == "at_edge"
            and next_loc_type is None
            and prev_loc_type == "at_edge"
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
            this_loc_type in ("at_vertex", "at_edge")
            and next_loc_type != "interior"
        ):
            continue
        elif (
            this_loc_type == "at_vertex"
            and next_loc_type == "at_edge"
            and next_loc_ix >= 0
        ):
            edge = poly_edges[next_loc_ix]
            d = distance_point_to_edge(
                ptest = this_pt,
                pt1 = edge[0],
                pt2 = edge[1],
            )
            if np.isclose(d, 0):
                continue
            else:
                new_points.append(this_pt)
        elif (
            this_loc_type == "at_edge"
            and next_loc_type == "at_vertex"
            and next_pt is not None
        ):
            edge = poly_edges[this_loc_ix]
            d = distance_point_to_edge(
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


@njit
def slicing_point_location(
    pts: PointType,
    slicing_pts: PointType,
    poly_edges: PointType,  # It is calculated in the parent function so we don't want to recalc.
) -> dict:
    """Returns the location of each slicing point.

    The returned dict has the following format:
    `{slicing_point_index: (location_string, location_index)}`.
    `location_index` is either vertex index, edge index, or `-1` (for `interior`).
    `location_string` is `at_vertex`, `at_edge`, or `interior`.

    Example return values:
    - `{0: ("at_vertex", 2)}` - slicing point 0 is at vertex 2
    - `{1: ("at_edge", 1)}` - slicing point 0 is at edge 1
    - `{2: ("interior", -1)}` - slicing point 2 is inside the polygon

    The number of itmes in the dict is equal to the number of slicing points.

    Args:
        pts: polygon points
        slicing_pts: points defining how to slice the polygon
        poly_edges: list of tuples of points defining the polygon edges

    Return:
        dict defining the location of each slicing point (vertex, edge, interior)
    """
    if len(slicing_pts) == 0:
        raise GeometryError("No slicing points passed")

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
