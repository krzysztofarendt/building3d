import numpy as np
from numba import njit

from building3d.config import EPSILON
from building3d.config import GEOM_ATOL
from building3d.config import GEOM_RTOL
from building3d.config import POINT_NUM_DEC
from building3d.geom.exceptions import GeometryError
from building3d.geom.exceptions import TriangulationError
from building3d.geom.points import are_points_collinear
from building3d.geom.points import is_point_inside_bbox
from building3d.geom.types import INT
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.types import VectorType


@njit
def triangle_area(pt1: PointType, pt2: PointType, pt3: PointType) -> float:
    """Calculates triangle area using the Heron's formula.

    Reference: https://en.wikipedia.org/wiki/Heron%27s_formula
    """
    va = pt2 - pt1
    vb = pt3 - pt2
    vc = pt3 - pt1
    a = np.linalg.norm(va)
    b = np.linalg.norm(vb)
    c = np.linalg.norm(vc)

    s = 0.5 * (a + b + c)
    area = np.sqrt(s * (s - a) * (s - b) * (s - c) + EPSILON)

    return area


@njit
def triangle_centroid(pt1: PointType, pt2: PointType, pt3: PointType) -> PointType:
    """Calculates triangle's centroid. It is simply a mean of its vertices."""
    return (pt1 + pt2 + pt3) / 3.0


@njit
def is_point_on_same_side(
    pt1: PointType,
    pt2: PointType,
    ptest: PointType,
    ptref: PointType,
    atol: float = GEOM_ATOL,
) -> bool:
    """Tests if ptest is on the same side of the vector p1->p2 as ptref.

    Args:
        pt1: first vertex of the vector
        pt2: second vertex of the vector
        ptest: tested point (does it lie on the same side as ptref?)
        ptref: reference point
        atol: absolute tolerance

    Returns:
        True if ptest is on the same side as ptref

    Raises:
        GeometryError
    """
    vtest = np.cross(pt2 - pt1, ptest - pt1)
    vref = np.cross(pt2 - pt1, ptref - pt1)

    len_vtest = np.linalg.norm(vtest)
    len_vref = np.linalg.norm(vref)

    if len_vref < atol:
        # Wrong reference point chosen (collinear with p1 and p2)
        raise GeometryError("Wrong reference point chosen (colinear with p1 and p2)")
    elif len_vtest < atol:
        # This point lies on the edge connecting p1 and p2
        return False
    else:
        vtest /= len_vtest
        vref /= len_vref
        return bool(np.isclose(vtest, vref, atol=atol).all())


@njit
def is_point_inside(
    ptest: PointType,
    pt1: PointType,
    pt2: PointType,
    pt3: PointType,
    atol: float = GEOM_ATOL,
) -> bool:
    """Tests if point `ptest` is inside the triangle `(pt1, pt2, pt3)`.

    Using the "same side technique" described at:
    https://blackpawn.com/texts/pointinpoly/

    This function does not test if the point is coplanar with the triangle.
    """
    # Check if point is inside the bounding box
    if not is_point_inside_bbox(ptest, np.vstack((pt1, pt2, pt3)), atol=atol):
        return False

    # Test if the point is at any of the three vertices
    if (
        np.allclose(ptest, pt1, atol=atol)
        or np.allclose(ptest, pt2, atol=atol)
        or np.allclose(ptest, pt3, atol=atol)
    ):
        return True

    # Test if it's at any of the edges
    for pair in [(pt1, pt2), (pt2, pt3), (pt3, pt1)]:
        pts = np.vstack((pair[0], pair[1], ptest))
        if are_points_collinear(pts, atol=atol):
            # ptest is collinear, but is it on the edge or outside the triangle?
            xt, yt, zt = np.round(ptest, POINT_NUM_DEC)  # TODO: is np.round needed?
            x0, y0, z0 = np.round(pair[0], POINT_NUM_DEC)  # TODO: is np.round needed?
            x1, y1, z1 = np.round(pair[1], POINT_NUM_DEC)  # TODO: is np.round needed?
            if (
                xt > max(x0, x1) + atol
                or yt > max(y0, y1) + atol
                or zt > max(z0, z1) + atol
                or xt < min(x0, x1) - atol
                or yt < min(y0, y1) - atol
                or zt < min(z0, z1) - atol
            ):
                return False
            else:
                return True

    # Test if ptest is inside
    side1 = is_point_on_same_side(pt1, pt2, ptest, pt3, atol=atol)
    side2 = is_point_on_same_side(pt2, pt3, ptest, pt1, atol=atol)
    side3 = is_point_on_same_side(pt3, pt1, ptest, pt2, atol=atol)
    is_inside = side1 and side2 and side3

    if is_inside:
        return True
    else:
        return False


@njit
def is_corner_convex(
    pt1: PointType,
    pt2: PointType,
    pt3: PointType,
    vn: VectorType,
    atol: float = GEOM_ATOL,
) -> bool:
    """Checks if the angle between pt2->pt1 and pt2->pt3 is less than 180 degress.

    It is done by comparing the polygon normal vector with the cross product pt2->pt3 x pt2->pt1.
    The points pt1, pt2, pt3 should be ordered counter-clockwise with respect to the
    surface front side.

    Args:
        pt1: first corner point
        pt2: second corner point
        pt3: third corner point
        vn: unit vector normal to the surface defined by (pt1, pt2, pt3)
        atol: absolute tolerance

    Returns:
        True if the corner is convex, else False
    """
    assert (
        np.abs(np.linalg.norm(vn) - 1.0) < atol
    ), "Normal vector doesn't have a unit length"
    v1 = pt2 - pt1
    v2 = pt3 - pt2
    v1v2_n = np.cross(
        v1, v2
    )  # NOTE: different order in building3d.geom.triangle.is_corner_convex
    v1v2_n_len = np.linalg.norm(v1v2_n)

    if v1v2_n_len < atol:
        # Collinear points pt1, pt2, pt3
        return False
    else:
        # Normalize before comparing to vn
        v1v2_n /= v1v2_n_len

    if np.allclose(v1v2_n, vn, rtol=GEOM_RTOL):
        # Convex vertex
        return True
    else:
        # Concave vertex
        return False


@njit
def triangulate(
    pts: PointType,
    vn: VectorType,
    num_try: int = 0,
) -> tuple[PointType, IndexType]:
    """Return a list of points and triangles (i, j, k) using the ear-clipping algorithm.

    (i, j, k) are the indices of the points.
    The polygon must not have any holes.
    The polygon can be non-convex.

    The points `pts` are returned because they may be flipped during triangulation.
    This is a recursive function. If it fails on `pts`, it calls itself with `pts[::-1]`.

    Args:
        points: list of points defining the polygon
        normal: vector normal to the polygon

    Returns:
        tuple of points and indices
    """
    if num_try >= 2:
        raise TriangulationError("Ear-clipping algorithm failed.")

    if np.isclose(np.linalg.norm(vn), 0):
        raise TriangulationError("Normal vector cannot have zero length")

    vertices = [(i, p) for i, p in enumerate(pts)]
    triangles = []
    pos = 0
    num_fail = 0

    while len(vertices) > 2:
        if num_fail > len(pts):
            # Try with flipped points
            return triangulate(pts[::-1], vn, num_try + 1)

        # If last vertix, start from the beginning
        if pos > len(vertices) - 1:
            pos = 0

        prev_pos = pos - 1 if pos > 0 else len(vertices) - 1
        next_pos = pos + 1 if pos < len(vertices) - 1 else 0

        prev_id, prev_pt = vertices[prev_pos]
        curr_id, curr_pt = vertices[pos]
        next_id, next_pt = vertices[next_pos]

        convex_corner = is_corner_convex(prev_pt, curr_pt, next_pt, vn)

        if convex_corner:
            # Check if no other point is within this triangle
            # Needed for non-convex polygons
            any_point_inside = False
            for i in range(0, len(vertices)):
                test_id = vertices[i][0]
                if test_id not in (prev_id, curr_id, next_id):
                    point_inside = is_point_inside(
                        pts[test_id],
                        pts[prev_id],
                        pts[curr_id],
                        pts[next_id],
                    )
                    if point_inside:
                        any_point_inside = True
                        # break
            if not any_point_inside:
                # Add triangle
                triangles.append((prev_id, curr_id, next_id))
                # Remove pos from index
                vertices.pop(pos)
                continue
            else:
                # There is some point inside this triangle
                # So it is not not an ear
                num_fail += 1
        else:
            # Non-convex corner
            num_fail += 1
        pos += 1

    return pts, np.array(triangles, dtype=INT)
