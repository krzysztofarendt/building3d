import numpy as np

from .point import Point
from .vector import to_vector
from .vector import length
from .exceptions import GeometryError


def triangle_area(p1: Point, p2: Point, p3: Point) -> float:
    """Calculate triangle area using the Heron's formula.

    Reference: https://en.wikipedia.org/wiki/Heron%27s_formula
    """
    vec_a = to_vector(p1, p2)
    vec_b = to_vector(p2, p3)
    vec_c = to_vector(p3, p1)
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


def _is_on_correct_side(ptest: Point, p1: Point, p2: Point, pref: Point) -> bool:
    """Test if ptest is on the same side of p1->p2 as pref."""

    vtest = np.cross(to_vector(p1, p2), to_vector(p1, ptest))
    vref = np.cross(to_vector(p1, p2), to_vector(p1, pref))

    len_vtest = length(vtest)
    len_vref = length(vref)

    eps = 1e-6
    if len_vref < eps:
        # Wrong reference point chosen (colinear with p1 and p2)
        raise GeometryError("Wrong reference point chosen (colinear with p1 and p2)")
    elif len_vtest < eps:
        # This point lies exactly on the boundary of the triangle
        return True
    else:
        vtest /= len_vtest
        vref /= len_vref
        return bool(np.isclose(vtest, vref).all())


def is_point_inside(ptest: Point, p1: Point, p2: Point, p3: Point) -> bool:
    """Test if point ptest is inside the triangle (p1, p2, p3).

    Using the "same side technique" described at:
    https://blackpawn.com/texts/pointinpoly/
    """
    side1 = _is_on_correct_side(ptest, p1, p2, p3)
    side2 = _is_on_correct_side(ptest, p2, p3, p1)
    side3 = _is_on_correct_side(ptest, p3, p1, p2)

    return side1 and side2 and side3
