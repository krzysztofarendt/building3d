"""Wall class"""

from building3d import random_id
from building3d.geom.polygon import Polygon
from building3d.geom.exceptions import GeometryError


class Wall:
    """A wall is a collection of polygons with additional attributes and methods.

    Polygons do not have to be coplanar.
    Polygons can have subpolygons (e.g. a wall with a window).

    Wall is used to model 1D phenomena (e.g. heat transfer).
    """
    def __init__(self, polygons: list[Polygon] = [], name: str | None = None):
        if name is None:
            name = random_id()

        self.name = name
        self.polygons = {}
        self.polygraph = {}

        for poly in polygons:
            self.add_polygon(poly)

    def get_parent_names(self) -> list[str]:
        return list(self.polygraph.keys())

    def get_polygons(self) -> list[Polygon]:
        return [self.polygons[name] for name in self.get_parent_names()]

    def get_subpolygons(self, parent: str) -> list[Polygon]:
        if parent in self.polygraph.keys():
            return [self.polygons[name] for name in self.polygraph[parent]]
        else:
            return []

    def add_polygon(self, poly: Polygon, parent: str | None = None):
        """Add polygon to the wall.

        A polygon can be a top-level (parent) polygon or a subpolygon.
        Only 1 level of subpolygons is allowed, i.e. a polygon cannot be
        a subpolygon to another subpolygon.

        A subpolygon must be entirely inside its parent polygon.

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

            # Assert polygon is inside parent polygon
            for p in poly.points:
                if not self.polygons[parent].is_point_inside(p):
                    raise GeometryError(f"Polygon {poly.name} is not entirely inside {parent}")
