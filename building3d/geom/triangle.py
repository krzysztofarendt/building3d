import numpy as np

from .point import Point
from .vector import Vector
from .exceptions import GeometryError


def triangle_area(p1: Point, p2: Point, p3: Point) -> float:
    """Calculate triangle area using the Heron's formula.

    Reference: https://en.wikipedia.org/wiki/Heron%27s_formula
    """
    vec_a = Vector(p1, p2)
    vec_b = Vector(p2, p3)
    vec_c = Vector(p3, p1)
    a = vec_a.length()
    b = vec_b.length()
    c = vec_c.length()

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

    vtest = np.cross(Vector(p1, p2).v, Vector(p1, ptest).v)
    vref = np.cross(Vector(p1, p2).v, Vector(p1, pref).v)

    len_vtest = Vector._length(vtest)
    len_vref = Vector._length(vref)

    eps = 1e-6
    if len_vref < eps:
        # Wrong reference point chosen (colinear with p1 and p2)
        raise GeometryError("Wrong reference point chosen (colinear with p1 and p2)")
    elif len_vtest < eps:
        # This point lies on the edge connecting p1 and p2
        # Add jitter (move ptest a bit)
        jitter = (np.random.random(3) - 0.5) * eps
        ptest_jitter = Point(ptest.x + jitter[0], ptest.y + jitter[1], ptest.z + jitter[2])
        return is_point_on_correct_side(ptest_jitter, p1 ,p2, pref)
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
        v = Vector(pair[0], pair[1])
        if v.is_point_colinear(ptest):
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
