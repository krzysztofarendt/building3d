import numpy as np

from .exceptions import GeometryError
from .point import Point
from .vector import to_vector


class Wall:
    """A wall is composed of a number of points.

    The points should be ordered based on the right-hand rule,
    so that the vector normal to the wall points outwards the space
    that the wall is attached to.
    """
    def __init__(self, name: str, points: list[Point]):
        self.name = name
        self.points = points

    def center_of_weight(self) -> np.ndarray:
        """This is not a true center of weight, but a mean position of all points."""
        center = np.array([0.0, 0.0, 0.0])
        for p in self.points:
            center += p.vector()
        center /= len(self.points)
        return center

    def normal(self) -> tuple[Point, Point]:
        """Calculate a unit normal vector for this wall.

        The vector origin is at the center of weight.
        The normal vector is calculated using the cross product
        of two vectors A and B spanning between points:
        - A: 0 -> 1 (first and second point)
        - B: 0 -> -1 (first and last point)
        """
        ctr = self.center_of_weight()
        vec_a = self.points[0].vector() - self.points[1].vector()
        vec_b = self.points[0].vector() - self.points[-1].vector()
        norm = np.cross(vec_a, vec_b)
        norm /= np.sqrt(norm[0] ** 2 + norm[1] ** 2 + norm[2] ** 2)
        norm += ctr

        normal_beg = Point(x=ctr[0], y=ctr[1], z=ctr[2])
        normal_end = Point(x=norm[0], y=norm[1], z=norm[2])

        return (normal_beg, normal_end)

    def edges(self) -> list[tuple[Point, Point]]:
        """Return a list of edges of this wall."""
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

    def are_points_coplanar(self) -> bool:
        vec_n = to_vector(*self.normal())

        # Plane equation:
        # ax + by + cz + d = 0
        # (a, b, c) are taken from the normal vector
        # d is calculated by substituting one of the points
        ref = 0  # reference point index
        ref_pt = self.points[ref]
        d = -1 * (vec_n[0] * ref_pt.x + vec_n[1] * ref_pt.y + vec_n[2] * ref_pt.z)

        # Check if all points lay on the same plane
        eps = 1e-6
        for pt in self.points:
            coplanar = np.abs(vec_n[0] * pt.x + vec_n[1] * pt.y + vec_n[2] * pt.z + d) < eps
            if not coplanar:
                return False
        return True

    def verify(self):
        """Verify geometry correctness."""
        # At least 3 points
        if len(self.points) < 3:
            raise GeometryError(f"Wall {self.name} has only {len(self.points)} points")

        # Check if all points are coplanar
        if not self.are_points_coplanar():
            raise GeometryError(f"Points of wall {self.name} aren't coplanar")
