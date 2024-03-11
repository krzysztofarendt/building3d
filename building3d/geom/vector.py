import numpy as np

from .point import Point


class Vector:
    def __init__(self, p1: Point, p2: Point):
        self.v = np.array([])
        self.update(p1, p2)

    def update(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.v = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])

    def length(self):
        return Vector._length(self.v)

    def attach(self, p: Point):
        self.update(self.p1 + p, self.p2 + p)

    def angle(self, other) -> float:
        return Vector._angle(self.v, other.v)

    def angle_ccw(self, other, n) -> float:
        return Vector._angle_ccw(self.v, other.v, n.v)

    def is_point_colinear(self, p) -> bool:
        v1 = np.array([self.p1.x - p.x, self.p1.y - p.y, self.p1.z - p.z])
        v2 = np.copy(self.v)
        v1 /= Vector._length(v1)
        v2 /= Vector._length(v2)
        eps = 1e-6
        if (np.abs(v1 - v2) < eps).all():
            # Test for vectors with the same direction
            return True
        elif (np.abs(v1 + v2) < eps).all():
            # Test for vectors directed opposite
            return True
        else:
            return False

    @staticmethod
    def _length(v: np.ndarray) -> float:
        """Calculate the length of the vector."""
        return np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)

    @staticmethod
    def _angle(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate angle in radians between two vectors.
        """
        rad = np.arccos(
            np.clip(
                np.dot(v1 / Vector._length(v1), v2 / Vector._length(v2)),
                -1.0,
                1.0,
            )
        )
        if rad < 0:
            rad = 2. * np.pi  + rad
        return rad

    @staticmethod
    def _angle_ccw(v1: np.ndarray, v2: np.ndarray, n: np.ndarray) -> float:
        """Calculate counter-clockwise angle in radians between two vectors.
        """
        # In 3D space, determining whether an angle is
        # counterclockwise or clockwise depends on the context and
        # the coordinate system being used.
        # That's why we need a fixed normal
        n /= Vector._length(n)
        assert (~np.isnan(n)).any(), "Normal has 0 length"

        dot = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
        det = np.dot(n, np.cross(v1, v2))
        rad = np.arctan2(det, dot)

        if rad < 0:
            rad = 2. * np.pi  + rad

        return rad
