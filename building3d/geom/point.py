"""Point class"""

import numpy as np


class Point:
    """Point is a simple class with three attributes: x, y, z."""

    eps = 1e-6

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def vector(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def __str__(self):
        return f"pt(x={self.x:.1f},y={self.y:.1f},z={self.z:.1f})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        x_eq = np.abs(self.x - other.x) < Point.eps
        y_eq = np.abs(self.y - other.y) < Point.eps
        z_eq = np.abs(self.z - other.z) < Point.eps

        if x_eq and y_eq and z_eq:
            return True
        else:
            return False

    def __add__(self, other):
        if len(other) == 3:
            return Point(self.x + other[0], self.y + other[1], self.z + other[2])
        else:
            raise TypeError("Point can be added only with a vector of length 3")
