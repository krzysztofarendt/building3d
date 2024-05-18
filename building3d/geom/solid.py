"""Solid class"""
from typing import Sequence

import numpy as np

from building3d import random_id
from building3d.geom.exceptions import GeometryError
from building3d.geom.wall import Wall
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.vector import vector
from building3d.geom.tetrahedron import tetrahedron_volume


class Solid:
    """Solid is a space enclosed by polygons."""
    # List of names of all Solid instances (names must be unique)
    instance_names = set()

    def __init__(self, walls: Sequence[Wall], name: str | None = None):
        if name is None:
            name = random_id()
        self.name = name
        self.walls = walls
        self._verify(throw=True)  # TODO: Slow for large models (e.g. teapot.stl)
        self.volume = self._volume()

    @staticmethod
    def add_name(name: str):
        if name not in Solid.instance_names:
            Solid.instance_names.add(name)
        else:
            raise ValueError(f"Solid {name} already exists!")

    @staticmethod
    def remove_name(name: str):
        if name in Solid.instance_names:
            Solid.instance_names.remove(name)

    def polygons(self, only_parents=True) -> list[Polygon]:
        """Return a list with all polygons of this solid."""
        poly = []
        for wall in self.walls:
            if only_parents:
                poly.extend(wall.get_polygons())
            else:
                poly.extend(wall.polygons.values())
        return poly

    def vertices(self) -> list[Point]:
        points = []
        for poly in self.polygons():
            points.extend(poly.points)
        return points

    def bounding_box(self) -> tuple[Point, Point]:
        """Return (Point(xmin, ymin, zmin), Point(xmax, ymax, zmax))"""
        points = self.vertices()
        xaxis = [p.x for p in points]
        yaxis = [p.y for p in points]
        zaxis = [p.z for p in points]
        pmin = Point(min(xaxis), min(yaxis), min(zaxis))
        pmax = Point(max(xaxis), max(yaxis), max(zaxis))
        return (pmin, pmax)

    def is_point_inside(self, p: Point) -> bool:
        """Checks whether the point p is inside the solid.

        Being at the boundary is assumed to be inside.

        Uses the ray casting algorithm:
        draw a horizontal line in a chosen direction from the point
        and count how many times it intersects with the edges of the
        solid; if the number of intersections is odd, it is inside.
        """
        vertices = self.vertices()
        max_x = max([p.x for p in vertices])
        max_y = max([p.y for p in vertices])
        max_z = max([p.z for p in vertices])
        min_x = min([p.x for p in vertices])
        min_y = min([p.y for p in vertices])
        min_z = min([p.z for p in vertices])

        # Check if it is possible that the point is inside the solid
        if p.x > max_x or p.y > max_y or p.z > max_z:
            return False
        if p.x < min_x or p.y < min_y or p.z < min_z:
            return False

        # It is possible, so we proceed with the ray casting algorithm
        # This algorithm may give wrong answer if the point lays in the corner
        vec = np.array([0.739, 0.239, 0.113])  # Just a random vector
        vec /= np.linalg.norm(vec)

        num_crossings = 0
        for poly in self.polygons():
            p_crosses_polygon = poly.is_point_inside_projection(p, vec)
            if p_crosses_polygon:
                num_crossings += 1

        if num_crossings % 2 == 1:
            return True
        else:
            # Check if point is at the boundary
            if self.is_point_at_the_boundary(p):
                return True
            else:
                return False

    def is_point_at_the_boundary(self, p: Point) -> bool:
        """Checks whether the point p lays on any of the boundary polygons."""
        for poly in self.polygons():
            if poly.is_point_inside(p):
                return True
        return False

    def is_adjacent_to_solid(self, sld) -> bool:
        """Checks if this solid is adjacent to another solid."""
        for this_poly in self.polygons():
            for other_poly in sld.polygons():
                if this_poly.is_facing_polygon(other_poly):
                    return True
        return False

    def distance_to_solid_points(self, p: Point) -> float:
        """Return minimum distance from test point `p` to solid points."""
        dist = np.inf
        for poly in self.polygons():
            dp = poly.distance_point_to_polygon_points(p)
            if dp < dist:
                dist = dp
        return dist

    def _volume(self) -> float:
        """Based on: http://chenlab.ece.cornell.edu/Publication/Cha/icip01_Cha.pdf"""
        total_volume = 0.0
        for poly in self.polygons():
            for tri in poly.triangles:
                p0 = Point(0.0, 0.0, 0.0)
                p1 = poly.points[tri[0]]
                p2 = poly.points[tri[1]]
                p3 = poly.points[tri[2]]
                v = tetrahedron_volume(p0, p1, p2, p3)

                pos_wrt_origin = np.dot(poly.normal, vector(p0, p1))
                if pos_wrt_origin == 0.0:
                    pos_wrt_origin = np.dot(poly.normal, vector(p0, p2))

                if pos_wrt_origin > 0:
                    sign = 1.0
                else:
                    sign = -1.0

                total_volume += sign * v

        return abs(total_volume)

    def _verify(self, throw: bool = False) -> None:
        """Verify geometry correctness.

        Tests:
            - run verify() for each wall
            - make sure each point is attached to at least 2 walls

        Args:
            throw: if True it will raise the first encountered exception
        """
        errors = []
        points = []

        # Check if all points are attached to at least 2 walls
        for poly in self.polygons():
            points.extend([p.vector() for p in poly.points])

        has_duplicates = np.array([False for _ in points])
        for i1 in range(len(points)):
            for i2 in range(i1 + 1, len(points)):
                if has_duplicates[i1] == False or has_duplicates[i2] == False:
                    if (points[i1] == points[i2]).all():
                        has_duplicates[i1] = True
                        has_duplicates[i2] = True

        if not has_duplicates.all():
            errors.append(GeometryError(f"Some points in solid {self.name} are attached to only 1 wall"))

        # Print encountered geometry errors
        for e in errors:
            print(e)

        # Raise the first exception
        if throw and len(errors) > 0:
            raise errors[0]

    def __del__(self):
        Solid.remove_name(self.name)

    def __str__(self):
        return f"Solid({self.name=}, {self.walls=})"
