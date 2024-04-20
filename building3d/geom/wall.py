"""Wall class"""

from .polygon import Polygon


class Wall:
    """A wall is a collection of polygons with additional attributes and methods.
    """
    def __init__(self, name: str):
        self.name = name
        self.polygons = {}
        self.polygraph = {}

    def add_polygon(self, poly: Polygon, parent: str | None = None):
        """Add polygon to the wall.

        A polygon can be a top-level (parent) polygon or a subpolygon.
        Only 1 level of subpolygons is allowed, i.e. a polygon cannot be
        a subpolygon to another subpolygon.

        Args:
            poly: polygon to be added
            parent: name of parent polygon if this is a subpolygon (default None)
        """
        self.polygons[poly.name] = poly
        if parent is None:
            # This might be a parent polygon
            self.polygraph[poly.name] = []
        else:
            # Add this polygon to its parent
            self.polygraph[parent].append(poly.name)
