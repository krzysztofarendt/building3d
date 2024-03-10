import numpy as np

from .point import Point


def to_vector(p1: Point, p2: Point) -> np.ndarray:
    """Convert two points to a vector."""
    vec = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
    return vec


def length(v: np.ndarray) -> float:
    """Calculate the length of the vector."""
    return np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate angle in radians between two vectors."""
    rad = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
    if rad < 0:
        rad = 2. * np.pi  + rad
    return rad
