import numpy as np

from .point import Point
from .vector import to_vector
from .vector import length


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
