import numpy as np

from .point import Point
from .polygon import Polygon


class Wall(Polygon):
    """A wall is composed of a number of points.

    The points should be ordered based on the right-hand rule,
    so that the vector normal to the wall points outwards the space
    that the wall is attached to.
    """
    def __init__(self, name: str, points: list[Point]):
        super().__init__(points)
        self.name = name
