from typing import Sequence

from building3d import random_id
from building3d.geom.exceptions import GeometryError
from building3d.geom.paths import PATH_SEP
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.bboxes import bounding_box
from building3d.geom.polygon import Polygon
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.wall.get_mesh import get_mesh_from_polygons


class Wall:
    """A wall is a collection of polygons.

    Polygons do not have to be coplanar.
    """

    count: int = 0

    def __init__(
        self,
        polygons: Sequence[Polygon] = (),
        name: str | None = None,
        uid: str | None = None,
        parent=None,
    ):
        """Initialize the wall.

        Args:
            polygons: list of Polygon instances
            name: name of the wall, random if None
            uid: unique id of the wall, random if None
        """
        self._parent = parent

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

        self.num = Wall.count
        Wall.count += 1

    @property
    def children(self) -> dict[str, Polygon]:
        return self.polygons

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, sld):
        self._parent = sld

    @property
    def path(self) -> str:
        if self.parent is not None:
            p = PATH_SEP.join([self.parent.path, self.name])
            return p
        else:
            return self.name

    def add_polygon(self, poly: Polygon):
        """Add polygon to the wall.

        Args:
            poly: polygon to be added
        """
        if poly.name in self.polygons.keys():
            raise GeometryError(f"Polygon {poly.name} already exists in the wall")

        poly.parent = self
        self.polygons[poly.name] = poly

    def replace_polygon(self, old_name: str, *new_poly: Polygon):
        del self.polygons[old_name]
        for np in new_poly:
            self.add_polygon(np)

    def get(self, abspath: str):
        """Get object by the absolute path."""
        obj = self
        while obj.parent is not None:
            obj = obj.parent
        building = obj
        return building.get(abspath)

    def bbox(self) -> tuple[PointType, PointType]:
        pts, _ = self.get_mesh()
        return bounding_box(pts)

    def get_mesh(self) -> tuple[PointType, IndexType]:
        """Get vertices and faces of this wall's polygons.

        This function returns faces generated by the ear-clipping algorithm.

        Return:
            tuple of vertices, shaped (num_pts, 3), and faces, shaped (num_tri, 3)
        """
        return get_mesh_from_polygons(list(self.children.values()))

    def __str__(self):
        return f"Wall(name={self.name}, polygons={list(self.children.keys())}, id={hex(id(self))})"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key) -> Polygon:
        return self.polygons[key]
