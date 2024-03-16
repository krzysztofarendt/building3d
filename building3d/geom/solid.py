"""Solid class"""
from typing import Sequence

import numpy as np

from .exceptions import GeometryError
from .polygon import Polygon
from .point import Point


class Solid:
    """Solid is a space enclosed by polygons."""

    def __init__(self, boundary: Sequence[Polygon]):
        self.boundary = boundary
        self._verify(throw=True)

    def vertices(self):
        points = []
        for poly in self.boundary:
            points.extend(poly.points)
        return points

    def is_point_inside(self, p: Point) -> bool:
        """Checks whether the point p is inside the solid.

        Uses the ray casting algorithm:
        draw a horizontal line in a chosen direction from the point
        and count how many times it intersects with the edges of the
        solid; if the number of intersections is odd, it is inside.
        """
        vertices = self.vertices()
        max_x = max([p.x for p in vertices])
        max_y = max([p.y for p in vertices])
        max_z = max([p.z for p in vertices])
        min_x = min([p.x for p in vertices])
        min_y = min([p.y for p in vertices])
        min_z = min([p.z for p in vertices])

        # Check if it is possible that the point is inside the solid
        if p.x > max_x or p.y > max_y or p.z > max_z:
            return False
        if p.x < min_x or p.y < min_y or p.z < min_z:
            return False

        # It is possible, so we proceed with the ray casting algorithm
        vec = np.array([1.0, 0.0, 0.0])
        num_crossings = 0
        for poly in self.boundary:
            p_crosses_polygon = poly.is_point_inside_projection(p, vec)
            if p_crosses_polygon:
                num_crossings += 1

        if num_crossings % 2 == 1:
            return True
        else:
            return False

    def _verify(self, throw: bool = False) -> None:
        """Verify geometry correctness.

        Tests:
            - run verify() for each wall
            - make sure each point is attached to at least 2 walls

        Args:
            throw: if True it will raise the first encountered exception
        """
        errors = []
        points = []

        # Verify each wall
        for wall in self.boundary:
            points.extend([p.vector() for p in wall.points])

        # Check if all points are attached to at least 2 walls
        has_duplicates = np.array([False for _ in points])
        for i1 in range(len(points)):
            for i2 in range(i1 + 1, len(points)):
                if has_duplicates[i1] == False or has_duplicates[i2] == False:
                    if (points[i1] == points[i2]).all():
                        has_duplicates[i1] = True
                        has_duplicates[i2] = True

        if not has_duplicates.all():
            errors.append(GeometryError("Some points are attached to only 1 wall"))

        # Print encountered geometry errors
        for e in errors:
            print(e)

        # Raise the first exception
        if throw and len(errors) > 0:
            raise errors[0]
