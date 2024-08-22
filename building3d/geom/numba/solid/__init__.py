import logging
from typing import Sequence

import numpy as np

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.numba.points import bounding_box
from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.ispointinside import is_point_inside_projection
from building3d.geom.numba.polygon.facing import are_polygons_facing
from building3d.geom.numba.tetrahedrons import tetrahedron_volume
from building3d.geom.numba.solid.get_mesh import get_mesh_from_walls


logger = logging.getLogger(__name__)


class Solid:
    """Solid is a space enclosed by polygons."""
    def __init__(
        self,
        walls: Sequence[Wall] = (),
        name: str | None = None,
        uid: str | None = None,
    ):
        """Initialize the solid

        Args:
            walls: list of Wall instances
            name: name of the solid
            uid: unique id of the solid, random if None
        """
        if name is None:
            name = random_id()
        self.name = validate_name(name)
        if uid is not None:
            self.uid = uid
        else:
            self.uid = random_id()
        self.walls: dict[str, Wall] = {}  # {Wall.name: Wall}
        for w in walls:
            self.add_wall(w)

    def add_wall(self, wall: Wall) -> None:
        """Add a Wall instance to the solid."""
        self.walls[wall.name] = wall

    def replace_wall(self, old_name: str, new_wall: Wall):
        del self.walls[old_name]
        self.add_wall(new_wall)

    def get_wall_names(self) -> list[str]:
        """Get list of wall names."""
        return list(self.walls.keys())

    def get_walls(self) -> list[Wall]:
        """Get list of walls."""
        return list(self.walls.values())

    def get_object(self, path: str) -> Wall | Polygon:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        wall_name = names.pop(0)

        if wall_name not in self.get_wall_names():
            raise ValueError(f"Wall not found: {wall_name}")
        elif len(names) == 0:
            return self.walls[wall_name]
        else:
            return self.walls[wall_name].get_object("/".join(names))

    def get_mesh(self) -> tuple[PointType, IndexType]:
        """Get vertices and faces of this solid's walls.

        This function returns faces generated by the ear-clipping algorithm.

        Return:
            tuple of vertices, shaped (num_pts, 3), and faces, shaped (num_tri, 3)
        """
        return get_mesh_from_walls(self.get_walls())

    def bbox(self) -> tuple[PointType, PointType]:
        pts, _ = self.get_mesh()
        return bounding_box(pts)

    def is_point_inside(self, pt: PointType) -> bool:  # TODO: use numba
        """Checks whether the point p is inside the solid.

        Being at the boundary is assumed to be inside.

        Uses the ray casting algorithm:
        draw a horizontal line in a chosen direction from the point
        and count how many times it intersects with the edges of the
        solid; if the number of intersections is odd, it is inside.
        """
        vertices, _ = self.get_mesh()
        max_x = vertices[:, 0].max()
        max_y = vertices[:, 1].max()
        max_z = vertices[:, 2].max()
        min_x = vertices[:, 0].min()
        min_y = vertices[:, 1].min()
        min_z = vertices[:, 2].min()

        # Check if it is possible that the point is inside the solid
        if pt[0] > max_x or pt[1] > max_y or pt[2] > max_z:
            return False
        if pt[0] < min_x or pt[1] < min_y or pt[2] < min_z:
            return False

        # It is possible, so we proceed with the ray casting algorithm
        # This algorithm may give wrong answer if the point lays in the corner
        vec = np.array([0.739, 0.239, 0.113])  # Just a random vector
        vec /= np.linalg.norm(vec)

        num_crossings = 0
        all_polys = [p for w in self.get_walls() for p in w.get_polygons()]
        for poly in all_polys:
            p_crosses_polygon = is_point_inside_projection(pt, vec, poly.pts, poly.tri)
            if p_crosses_polygon:
                num_crossings += 1

        if num_crossings % 2 == 1:
            return True
        else:
            # Check if point is at the boundary
            if self.is_point_at_boundary(pt):
                return True
            else:
                return False

    def is_point_at_boundary(self, pt: PointType) -> bool:
        """Checks whether the point p lays on any of the boundary polygons."""
        all_polys = [p for w in self.get_walls() for p in w.get_polygons()]
        for poly in all_polys:
            if poly.is_point_inside(pt):
                return True
        return False

    def is_adjacent_to_solid(self, sld, exact: bool = True) -> bool:
        """Checks if this solid is adjacent to another solid.

        The argument `exact` has the same meaning as in Polygon.is_facing_polygon().
        If `exact` is True, all points of adjacent polygons must be equal.
        If `exact` is False, the method checks only in points are coplanar and
        normal vectors are opposite.

        Args:
            sld: other solid
            exact: if True, the solid must be exactly adjacent

        Return:
            True if the solids are adjacent
        """
        # TODO: Polygons can be sorted based on the distance of their centroids
        this_all_polys = [p for w in self.get_walls() for p in w.get_polygons()]
        other_all_polys = [p for w in sld.get_walls() for p in w.get_polygons()]

        for this_poly in this_all_polys:
            for other_poly in other_all_polys:
                pts1 = this_poly.pts
                tri1 = this_poly.tri
                vn1 = this_poly.vn
                pts2 = other_poly.pts
                tri2 = other_poly.tri
                vn2 = other_poly.vn
                if are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2, exact=exact):
                    return True
        return False

    @property
    def volume(self) -> float:
        """Based on: http://chenlab.ece.cornell.edu/Publication/Cha/icip01_Cha.pdf"""
        total_volume = 0.0
        all_polys = [p for w in self.get_walls() for p in w.get_polygons()]
        for poly in all_polys:
            for tri in poly.tri:
                p0 = new_point(0.0, 0.0, 0.0)
                p1 = poly.pts[tri[0]]
                p2 = poly.pts[tri[1]]
                p3 = poly.pts[tri[2]]
                v = tetrahedron_volume(p0, p1, p2, p3)

                pos_wrt_origin = np.dot(poly.vn, p1 - p0)
                if pos_wrt_origin == 0.0:
                    pos_wrt_origin = np.dot(poly.vn, p2 - p0)

                if pos_wrt_origin > 0:
                    sign = 1.0
                else:
                    sign = -1.0

                total_volume += sign * v

        return abs(float(total_volume))

    def __str__(self):
        return f"Solid(name={self.name}, walls={self.get_wall_names()}, id={hex(id(self))})"

    def __repr__(self):
        return self.__str__()
