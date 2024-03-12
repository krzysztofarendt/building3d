import numpy as np

from .point import Point
from .polygon import Polygon


class Wall(Polygon):
    """A wall is composed of a number of points.

    The points should be ordered counter-clockwise w.r.t. to the
    zone to which this wall belongs.
    """
    def __init__(self, name: str, points: list[Point]):
        super().__init__(points)
        self.name = name
