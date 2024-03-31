"""Functions related to triangles."""
import numpy as np

from .point import Point
from .vector import vector
from .vector import length
from .vector import is_point_colinear
from .exceptions import GeometryError
from building3d.config import GEOM_EPSILON




def triangle_area(p1: Point, p2: Point, p3: Point) -> float:
    """Calculate triangle area using the Heron's formula.

    Reference: https://en.wikipedia.org/wiki/Heron%27s_formula
    """
    vec_a = vector(p1, p2)
    vec_b = vector(p2, p3)
    vec_c = vector(p3, p1)
    a = length(vec_a)
    b = length(vec_b)
    c = length(vec_c)

    s = 0.5 * (a + b + c)
    area = np.sqrt(s * (s - a) * (s - b) * (s - c))

    return area


def triangle_centroid(p1: Point, p2: Point, p3: Point) -> Point:
    cx = (p1.x + p2.x + p3.x) / 3.
    cy = (p1.y + p2.y + p3.y) / 3.
    cz = (p1.z + p2.z + p3.z) / 3.

    return Point(cx, cy, cz)


def is_point_on_correct_side(ptest: Point, p1: Point, p2: Point, pref: Point) -> bool:
    """Test if ptest is on the same side of p1->p2 as pref."""

    vtest = np.cross(vector(p1, p2), vector(p1, ptest))
    vref = np.cross(vector(p1, p2), vector(p1, pref))

    len_vtest = length(vtest)
    len_vref = length(vref)

    if len_vref < GEOM_EPSILON:
        # Wrong reference point chosen (colinear with p1 and p2)
        raise GeometryError("Wrong reference point chosen (colinear with p1 and p2)")
    elif len_vtest < GEOM_EPSILON:
        # This point lies on the edge connecting p1 and p2
        # Add jitter (move ptest a bit)
        jitter = (np.random.random(3) - 0.5) * GEOM_EPSILON
        ptest_jitter = Point(ptest.x + jitter[0], ptest.y + jitter[1], ptest.z + jitter[2])
        return is_point_on_correct_side(ptest_jitter, p1, p2, pref)
    else:
        vtest /= len_vtest
        vref /= len_vref
        return bool(np.isclose(vtest, vref).all())


def is_point_inside(ptest: Point, p1: Point, p2: Point, p3: Point) -> bool:
    """Test if point ptest is inside the triangle (p1, p2, p3).

    Using the "same side technique" described at:
    https://blackpawn.com/texts/pointinpoly/

    This function does not test if the point is coplanar with the triangle.
    """
    # Test if the point is at any of the three vertices
    if ptest == p1 or ptest == p2 or ptest == p3:
        return True

    # Test if it's at any of the edges
    for pair in [(p1, p2), (p2, p3), (p3, p1)]:
        if is_point_colinear(pair[0], pair[1], ptest):
            # Is colinear, but is it on the edge or outside the triangle?
            if (
                ptest.x > max(pair[0].x, pair[1].x) or \
                ptest.y > max(pair[0].y, pair[1].y) or \
                ptest.z > max(pair[0].z, pair[1].z) or \
                ptest.x < min(pair[0].x, pair[1].x) or \
                ptest.y < min(pair[0].y, pair[1].y) or \
                ptest.z < min(pair[0].z, pair[1].z)
            ):
                return False
            else:
                return True

    # Test if it's inside
    side1 = is_point_on_correct_side(ptest, p1, p2, p3)
    side2 = is_point_on_correct_side(ptest, p2, p3, p1)
    side3 = is_point_on_correct_side(ptest, p3, p1, p2)

    is_inside = side1 and side2 and side3
    if is_inside:
        return True

    # It must be outside
    return False


def triangulate(points: list[Point], normal: np.ndarray) -> list[int]:
    """Return a list of triangles (i, j, k) using the ear clipping algorithm.

    (i, j, k) are the indices of the points.
    The polygon must not have any holes.
    The polygon can be non-convex.

    Args:
        points: list of points defining the polygon
        normal: vector normal to the polygon
    """
    def is_convex(p0: Point, p1: Point, p2: Point, n: np.ndarray) -> bool:
        """Check if the angle between p1->p0 and p1->p2 is less than 180 degress.

        It is done by comparing the polygon normal vector with the
        cross product p1->p2 x p1->p0.
        """
        assert np.abs(length(n) - 1.) < GEOM_EPSILON
        v1 = vector(p1, p2)
        v2 = vector(p1, p0)
        v1_v2_normal = np.cross(v1, v2)
        len_v1_v2 = length(v1_v2_normal)
        if len_v1_v2 < GEOM_EPSILON:
            # Colinear points p0, p1, p2
            return False
        else:
            # Normalize before comparing to n
            v1_v2_normal /= length(v1_v2_normal)
        if np.isclose(v1_v2_normal, n).all():
            # Convex vertex
            return True
        else:
            # Concave vertex
            return False

    vertices = [(i, p) for i, p in enumerate(points)]
    triangles = []
    pos = 0

    number_failed = 0

    while len(vertices) > 2:

        if number_failed > len(vertices):
            raise RuntimeError("Triangulation failed, reason unknown :(")

        # If last vertix, start from the beginning
        if pos > len(vertices) - 1:
            pos = 0

        prev_pos = pos - 1 if pos > 0 else len(vertices) - 1
        next_pos = pos + 1 if pos < len(vertices) - 1 else 0

        prev_id, prev_pt = vertices[prev_pos]
        curr_id, curr_pt = vertices[pos]
        next_id, next_pt = vertices[next_pos]

        convex_corner = is_convex(prev_pt, curr_pt, next_pt, normal)

        if convex_corner:
            # Check if no other point is within this triangle
            # Needed for non-convex polygons
            any_point_inside = False

            for i in range(0, len(vertices)):
                test_id = vertices[i][0]
                if test_id not in (prev_id, curr_id, next_id):
                    point_inside = is_point_inside(
                        points[test_id],
                        points[prev_id],
                        points[curr_id],
                        points[next_id],
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
                number_failed += 1

        else:
            # Non-convex corner
            number_failed += 1

        pos += 1

    return triangles
