import numpy as np

from .point import Point
from .vector import length
from .vector import vector
from building3d.config import EPSILON
from building3d.config import MESH_DELTA


def tetrahedron_volume(p0: Point, p1: Point, p2: Point, p3: Point) -> float:
    """Volume calculation using the Cayley-Menger formula."""
    # Edge lengths
    a = length(vector(p0, p1))
    b = length(vector(p0, p2))
    c = length(vector(p0, p3))
    d = length(vector(p1, p2))
    e = length(vector(p2, p3))
    f = length(vector(p1, p3))

    x = (b ** 2 + c ** 2 - e ** 2)
    y = (a ** 2 + c ** 2 - f ** 2)
    z = (a ** 2 + b ** 2 - d ** 2)

    nominator = 4 * a**2 * b**2 * c**2 - a**2 * x ** 2 - b**2 * y ** 2 - c**2 * z ** 2 + x * y * z
    vol = np.sqrt(nominator + EPSILON) / 12.0

    return vol


def minimum_tetra_volume(delta: float = MESH_DELTA) -> float:
    """Calculate minimum tetrahedron volume for mesh quality assurance."""
    ref_volume = tetrahedron_volume(
        Point(0.0, 0.0, 0.0),
        Point(delta, 0.0, 0.0),
        Point(0.0, delta, 0.0),
        Point(0.0, 0.0, delta),
    )
    min_vol= ref_volume / 3.
    return min_vol


def tetrahedron_centroid(p0: Point, p1: Point, p2: Point, p3: Point) -> Point:
    """Centroid of a tetrahedron is just the average of its vertices."""
    c = (p0.vector() + p1.vector() + p2.vector() + p3.vector()) / 4
    cp = Point(c[0], c[1], c[2])
    return cp
