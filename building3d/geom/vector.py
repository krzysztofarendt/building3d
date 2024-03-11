import numpy as np

from .point import Point


class Vector:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = None
        self.p2 = None
        self.v = np.array([])
        self.update(p1, p2)

    def update(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.v = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])

    def length(self):
        return Vector._length(self.v)

    @staticmethod
    def _length(v: np.ndarray) -> float:
        """Calculate the length of the vector."""
        return np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)

    def angle(self, other) -> float:
        return Vector._angle(self.v, other.v)

    @staticmethod
    def _angle(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate angle in radians between two vectors.
        """
        rad = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
        if rad < 0:
            rad = 2. * np.pi  + rad
        return rad
