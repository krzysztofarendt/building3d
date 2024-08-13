import numpy as np
from typing import Sequence

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.exceptions import GeometryError


class Wall:
    """A wall is a collection of polygons with additional attributes and methods.

    Polygons do not have to be coplanar.
    Polygons can have subpolygons (e.g. a wall with a window).

    Wall is used to model 1D phenomena (e.g. heat transfer).
    """
    def __init__(
        self,
        polygons: Sequence[Polygon] = [],
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

    def get_polygon_names(self) -> list[str]:
        """Return list of parent polygon names."""
        return list(self.polygons.keys())

    def get_polygons(self) -> list[Polygon]:
        """Return list of all polygons."""
        return list(self.polygons.values())

    def get_object(self, path: str) -> Polygon | None:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        poly_name = names.pop(0)

        polygon_names_all = self.get_polygon_names()

        if poly_name not in polygon_names_all:
            raise ValueError(f"Polygon not found: {poly_name}")
        elif len(names) == 1:  # searching for subpolygon
            subpoly_name = names[0]
            if subpoly_name in polygon_names_all:
                return self.polygons[subpoly_name]
            else:
                raise ValueError(f"Subpolygon not found: {subpoly_name}")
        elif len(names) == 0:
            return self.polygons[poly_name]
        else:
            raise ValueError("Path to object too deep (too many slashes)")

    def get_mesh(self) -> tuple[PointType, IndexType]:
        """Get vertices and faces of this wall's polygons.

        This function returns faces generated by the ear-clipping algorithm.

        Return:
            tuple of vertices and faces
        """
        verts = []
        faces = []

        for poly in self.get_polygons():
            offset = len(verts)
            verts.extend(poly.pts.tolist())
            f = poly.tri + offset
            faces.extend(f.tolist())

        verts_arr = np.vstack(verts)
        faces_arr = np.array(faces)

        return verts_arr, faces_arr

    def __eq__(self, other):
        """Return True if all polygons of this and other are equal."""
        if len(self.polygons.values()) != len(other.polygons.values()):
            return False
        else:
            num_matches = 0
            for this_poly in self.polygons.values():
                for other_poly in other.polygons.values():
                    if this_poly == other_poly:
                        num_matches += 1
                        break
            if num_matches != len(self.polygons.values()):
                return False
        return True

    def __str__(self):
        return f"Wall(name={self.name}, polygons={self.polygons}, id={hex(id(self))})"

    def __repr__(self):
        return self.__str__()
