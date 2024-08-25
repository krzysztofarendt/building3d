"""Wall class"""

import numpy as np

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.exceptions import GeometryError


class Wall:
    """A wall is a collection of polygons with additional attributes and methods.

    Polygons do not have to be coplanar.
    Polygons can have subpolygons (e.g. a wall with a window).

    Wall is used to model 1D phenomena (e.g. heat transfer).
    """

    def __init__(
        self,
        polygons: list[Polygon] = [],
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

        # Graph of polygons and subpolygons
        # Keys are parent polygons, keys are subpolygons
        # Subpolygons are never added to keys
        self.polygraph: dict[str, list[str]] = {}  # {Polygon.name: [Polygon.name, ...]}

        for poly in polygons:
            self.add_polygon(poly)

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
        if poly.name in self.polygons.keys():
            raise GeometryError(f"Polygon {poly.name} already exists in the wall")

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
                    raise GeometryError(
                        f"Polygon {poly.name} is not entirely inside {parent}"
                    )

        # Sanity check
        if parent is not None:
            assert (
                poly.name not in self.polygraph.keys()
            ), "Subpolygon cannot be a parent polygon"

    def get_polygon_names(self, children=False) -> list[str]:
        """Return list of parent polygon names."""
        if children is False:
            return list(self.polygraph.keys())
        else:
            return list(self.polygons.keys())

    def get_polygons(self, children=False) -> list[Polygon]:
        """Return list of all polygons (parents and optionally subpolygons)."""
        return [
            self.polygons[name] for name in self.get_polygon_names(children=children)
        ]

    def get_subpolygons(self, parent: str) -> list[Polygon]:
        """Return list of subpolygons of the given parent polygon."""
        if parent in self.polygraph.keys():
            return [self.polygons[name] for name in self.polygraph[parent]]
        else:
            return []

    def get_parent_name(self, poly_name: str) -> str | None:
        """Return name of the parent polygon of the given subpolygon."""
        for parent_name in self.polygraph.keys():
            if poly_name in self.polygraph[parent_name]:
                return parent_name
        return None

    def get_object(self, path: str) -> Polygon | None:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        poly_name = names.pop(0)

        polygon_names_all = self.get_polygon_names(children=True)

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

    def get_mesh(
        self,
        children: bool = True,
    ) -> tuple[list[Point], list[list[int]]]:
        """Get vertices and faces of this wall's polygons.

        This function returns faces generated by the ear-clipping algorithm.

        Args:
            children: if True, parent and subpolygons are returned

        Return:
            tuple of vertices and faces
        """
        verts = []
        faces = []

        for poly in self.get_polygons(children=children):
            offset = len(verts)
            verts.extend(poly.points)
            f = np.array(poly.triangles) + offset
            f = [list(x) for x in f]
            faces.extend(f)

        return verts, faces

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
