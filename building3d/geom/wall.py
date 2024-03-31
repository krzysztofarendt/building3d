"""Wall class"""

from .point import Point
from .polygon import Polygon


class Wall(Polygon):
    """A wall is a subclass of Polygon with additional attributes and methods.

    The points should be ordered counter-clockwise w.r.t. to the
    zone to which this wall belongs.
    """
    def __init__(self, name: str, points: list[Point]):
        super().__init__(name, points)
