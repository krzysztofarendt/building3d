"""Point class"""
from typing import Sequence

import numpy as np


class Point:
    """Point is a simple class with three attributes: x, y, z."""

    eps = 1e-8

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def copy(self):
        """Return a copy of itself.

        Return:
            Point
        """
        return Point(self.x, self.y, self.z)

    def vector(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def add(self, vec: Sequence):
        if len(vec) != 3:
            raise TypeError("len(vec) must equal to 3")
        return Point(self.x + vec[0], self.y + vec[1], self.z + vec[2])

    def multiply(self, vec: Sequence):
        if len(vec) != 3:
            raise TypeError("len(vec) must equal to 3")
        return Point(self.x * vec[0], self.y * vec[1], self.z * vec[2])

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

    def __add__(self, other: Sequence):
        if (
                type(other) is list or \
                type(other) is tuple or \
                type(other) is np.ndarray \
        ) and (len(other) == 3):
            return self.add(other)
        elif type(other) is int or type(other) is float:
            raise TypeError(
                "float or int cannot be added to a Point. "
                "If you're trying to add a numpy array to a point (array + point), "
                "try reversing the order to (point + array) to avoid numpy's broadcasting."
            )
        else:
            raise TypeError("Point can be added only with a vector of length 3")

    def __radd__(self, other: Sequence):
        if type(other) is list or type(other) is tuple:
            return self.__add__(other)
        elif type(other) is int or type(other) is float:
            raise TypeError(
                "float or int cannot be added to a Point. "
                "If you're trying to add a numpy array to a point (array + point), "
                "try reversing the order to (point + array) to avoid numpy's broadcasting."
            )
        else:
            raise TypeError("Point can be added only with a vector of length 3")

    def __mul__(self, other: Sequence):
        if (
                type(other) is list or \
                type(other) is tuple or \
                type(other) is np.ndarray \
        ) and (len(other) == 3):
            return self.multiply(other)
        elif type(other) is int or type(other) is float:
            raise TypeError(
                "float or int cannot be added to a Point. "
                "If you're trying to multiply a numpy array with a point (array * point), "
                "try reversing the order to (point * array) to avoid numpy's broadcasting."
            )
        else:
            raise TypeError("Point can be added only with a vector of length 3")

    def __rmul__(self, other):
        if type(other) is list or type(other) is tuple:
            return self.__mul__(other)
        elif type(other) is int or type(other) is float:
            raise TypeError(
                "float or int cannot be multiplied with a Point. "
                "If you're trying to multiply a numpy array with a point (array * point), "
                "try reversing the order to (point * array) to avoid numpy's broadcasting."
            )
        else:
            raise TypeError("Point can be added only with a vector of length 3")
