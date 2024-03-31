"""Various functions related to vectors"""

import numpy as np

from .point import Point


def vector(p1: Point, p2: Point) -> np.ndarray:
    return np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])


def length(v: np.ndarray) -> float:
    return np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def normal(p0: Point, p1: Point, p2: Point) -> np.ndarray:
    n = np.cross(p1.vector() - p0.vector(), p2.vector() - p0.vector())
    n /= np.linalg.norm(n)
    return n


def angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate angle in radians between two vectors.
    """
    rad = np.arccos(
        np.clip(
            np.dot(v1 / length(v1), v2 / length(v2)),
            -1.0,
            1.0,
        )
    )
    if rad < 0:
        rad = 2. * np.pi  + rad
    return rad


def angle_ccw(v1: np.ndarray, v2: np.ndarray, n: np.ndarray) -> float:
    """Calculate counter-clockwise angle in radians between two vectors.
    """
    # In 3D space, determining whether an angle is
    # counterclockwise or clockwise depends on the context and
    # the coordinate system being used.
    # That's why we need a fixed normal
    n /= length(n)
    assert (~np.isnan(n)).any(), "Normal has 0 length"

    dot = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    det = np.dot(n, np.cross(v1, v2))
    rad = np.arctan2(det, dot)

    if rad < 0:
        rad = 2. * np.pi  + rad

    return rad


def is_point_colinear(p1: Point, p2: Point, ptest: Point) -> bool:
    v1 = vector(p1, p2)
    v2 = vector(p1, ptest)

    v1 /= length(v1)
    v2 /= length(v2)

    if np.isclose(v1, v2).all() or np.isclose(v1, v2 * -1).all():
        return True
    else:
        return False
