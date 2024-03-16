from typing import Sequence

import numpy as np

from .exceptions import GeometryError
from .polygon import Polygon
from .point import Point


class Solid:
    """Solid is a space enclosed by polygons."""

    def __init__(self, boundary: Sequence[Polygon]):
        self.boundary = boundary

    def is_point_inside(p: Point) -> bool:
        pass  # TODO

    def verify(self, throw: bool = False) -> None:
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
