import numpy as np

from .exceptions import GeometryError
from .point import Point


class Wall:
    def __init__(self, name: str, points: list[Point]):
        self.name = name
        self.points = points

    def center_of_weight(self) -> np.ndarray:
        center = np.array([0.0, 0.0, 0.0])
        for p in self.points:
            center += p.vector()
        center /= len(self.points)
        return center

    def normal(self) -> tuple[Point, Point]:
        ctr = self.center_of_weight()
        v1 = self.points[0].vector() - self.points[1].vector()
        v2 = self.points[0].vector() - self.points[-1].vector()
        norm = np.cross(v1, v2)
        norm /= np.sqrt(norm[0] ** 2 + norm[1] ** 2 + norm[2] ** 2)
        norm += ctr

        normal_beg = Point(x=ctr[0], y=ctr[1], z=ctr[2])
        normal_end = Point(x=norm[0], y=norm[1], z=norm[2])

        return (normal_beg, normal_end)

    def line_segments(self) -> list[tuple[Point, Point]]:
        """Return a list of line segments composing this wall."""
        wall_line_segments = []
        segment = []

        i = 0
        while i < len(self.points):
            segment.append(self.points[i])
            i += 1

            if len(segment) == 2:
                wall_line_segments.append(tuple(segment))
                segment = []
                i -= 1

        return wall_line_segments

    def verify(self):
        """Verify geometry correctness."""
        if len(self.points) < 3:
            raise GeometryError(f"Wall {self.name} has only {len(self.points)} points")
