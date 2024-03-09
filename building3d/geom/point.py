import numpy as np


class Point:
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
