from typing import Sequence

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.numba.points import bounding_box
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.exceptions import GeometryError
from building3d.geom.numba.wall.get_mesh import get_mesh_from_polygons


class Wall:
    """A wall is a collection of polygons with additional attributes and methods.

    Polygons do not have to be coplanar.
    Polygons can have subpolygons (e.g. a wall with a window).

    Wall is used to model 1D phenomena (e.g. heat transfer).
    """
    def __init__(
        self,
        polygons: Sequence[Polygon] = (),
        name: str | None = None,
        uid: str | None = None,
    ):
        """Initialize the wall.

        Args:
            polygons: list of Polygon instances
            name: name of the wall, random if None
            uid: unique id of the wall, random if None
        """
        if name is None:
            name = random_id()

        self.name = validate_name(name)
        if uid is not None:
            self.uid = uid
        else:
            self.uid = random_id()

        self.polygons: dict[str, Polygon] = {}  # {Polygon.name: Polygon}

        for poly in polygons:
            self.add_polygon(poly)

    def add_polygon(self, poly: Polygon):
        """Add polygon to the wall.

        Args:
            poly: polygon to be added
        """
        if poly.name in self.polygons.keys():
            raise GeometryError(f"Polygon {poly.name} already exists in the wall")

        self.polygons[poly.name] = poly

    def replace_polygon(self, old_name: str, *new_poly: Polygon):
        del self.polygons[old_name]
        for np in new_poly:
            self.add_polygon(np)

    def get_polygon_names(self) -> list[str]:
        """Return list of parent polygon names."""
        return list(self.polygons.keys())

    def get_polygons(self) -> list[Polygon]:
        """Return list of all polygons."""
        return list(self.polygons.values())

    def get_object(self, path: str) -> Polygon:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        poly_name = names.pop(0)

        if poly_name not in self.get_polygon_names():
            raise ValueError(f"Polygon not found: {poly_name}")
        elif len(names) == 0:
            return self.polygons[poly_name]
        else:
            raise ValueError("Path to object too deep (too many slashes)")

    def bbox(self) -> tuple[PointType, PointType]:
        pts, _ = self.get_mesh()
        return bounding_box(pts)

    def get_mesh(self) -> tuple[PointType, IndexType]:
        """Get vertices and faces of this wall's polygons.

        This function returns faces generated by the ear-clipping algorithm.

        Return:
            tuple of vertices, shaped (num_pts, 3), and faces, shaped (num_tri, 3)
        """
        return get_mesh_from_polygons(self.get_polygons())

    def __str__(self):
        return f"Wall(name={self.name}, polygons={self.get_polygon_names()}, id={hex(id(self))})"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key) -> Polygon:
        return self.polygons[key]
