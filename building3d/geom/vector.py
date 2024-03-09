import numpy as np

from .point import Point


def to_vector(p1: Point, p2: Point) -> np.ndarray:
    vec = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
    return vec
