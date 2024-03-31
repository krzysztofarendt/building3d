"""Polygon class"""
import numpy as np

from .exceptions import GeometryError
from .point import Point
from .vector import vector
from .vector import length
from .triangle import triangle_centroid
from .triangle import triangle_area
from .triangle import is_point_inside as is_point_inside_triangle
from .triangle import triangulate
from building3d import random_id
from building3d.config import GEOM_EPSILON


class Polygon:
    """Polygon defined by its vertices (Point instances).

    Notes:
    - The first point must lay in the convex corner!
    - If used as a wall, the points should be ordered counter-clockwise w.r.t.
      to the zone that this wall belongs to.
    """
    # List of names of all Polygon instances (names must be unique)
    instance_names = set()

    def __init__(self, name: str, points: list[Point]):
        self.name = name
        Polygon.add_name(name)

        self.points = list(points)
        self.normal = self._normal()
        self._verify()
        self.triangles = self._triangulate()
        self.centroid = self._centroid()
        self.edges = self._edges()
        self.area = self._area()

    @staticmethod
    def add_name(name: str):
        if name not in Polygon.instance_names:
            Polygon.instance_names.add(name)
        else:
            raise ValueError(f"Polygon {name} already exists!")

    @staticmethod
    def remove_name(name: str):
        if name in Polygon.instance_names:
            Polygon.instance_names.remove(name)

    def copy(self, new_name: str):
        """Return a deep copy of itself.

        Args:
            new_name: polygon name (must be unique)

        Return:
            Polygon
        """
        return Polygon(new_name, [Point(p.x, p.y, p.z) for p in self.points])

    def points_as_array(self) -> np.ndarray:
        """Returns a copy of the points as a numpy array."""
        return np.array([[p.x, p.y, p.z] for p in self.points])

    def move_orthogonal(self, d: float) -> None:
        vec = self.normal * d
        for i in range(len(self.points)):
            self.points[i] += vec

    def plane_equation_coefficients(self) -> tuple:
        """Returns [a, b, c, d] from the equation ax + by + cz + d = 0.

        This equation describes the plane that this polygon is on.
        """
        return self.projection_coefficients(self.points[0])

    def projection_coefficients(self, p: Point) -> tuple:
        """Returns [a, b, c, d] from the equation ax + by + cz + d = 0.

        Uses the vector normal to this polygon and the point p
        to calculate the coefficients of the plane equation
        with the same slope as this polygon, but translated to the point p.
        """
        a = self.normal[0]
        b = self.normal[1]
        c = self.normal[2]

        d = -1 * (a * p.x + b * p.y + c * p.z)
        return (a, b, c, d)

    def plane_normal_and_d(self) -> tuple[np.ndarray, float]:
        """Return the normal vector and coefficient d describing the plane."""
        _, _, _, d = self.plane_equation_coefficients()
        return (self.normal, d)

    def is_point_coplanar(self, p: Point) -> bool:
        """Checks whether the point p is coplanar with the polygon."""
        # Temporarily add the test point to self.points
        self.points.append(p)
        is_coplanar = self._are_points_coplanar()
        # Remove the test point from self.points
        self.points = self.points[:-1]

        return is_coplanar

    def is_point_inside(self, p: Point) -> bool:
        """Checks whether a point lies on the surface of the polygon."""

        if not self.is_point_coplanar(p):
            return False

        for triangle_indices in self.triangles:
            tri = [self.points[i] for i in triangle_indices]

            if is_point_inside_triangle(p, tri[0], tri[1], tri[2]):
                return True

        return False

    def is_point_inside_ortho_projection(self, p: Point) -> bool:
        """Checks whether an orthogonally projected point hits the surface.

        The point is projected orthogonally to the polygon's plane.
        If the projected point is inside the polygon, return True.
        """
        # Translate polygon's to the point p
        a, b, c, d = self.plane_equation_coefficients()
        ap, bp, cp, dp = self.projection_coefficients(p)

        assert np.isclose(a, ap), "If a and ap are not equal, d should be normalized"
        assert np.isclose(b, bp), "If b and bp are not equal, d should be normalized"
        assert np.isclose(c, cp), "If c and cp are not equal, d should be normalized"

        # Distance
        # Negative distance -> point behind the polygon
        # Positive distance -> point in front of the polygon
        dist = d - dp

        # Make a copy of the polygon and move it to the point p
        poly_at_p = self.copy(random_id())
        poly_at_p.move_orthogonal(dist)
        assert poly_at_p.is_point_coplanar(p)

        # Check if the point lays inside the polygon
        is_inside = poly_at_p.is_point_inside(p)

        del poly_at_p
        return is_inside

    def is_point_inside_projection(
        self,
        p: Point,
        vec: np.ndarray,
        fwd_only: bool = True
    ) -> bool:
        """Checks whether a projected point hits the surface.

        The point is projected along the vector vec.
        It is possible to consider both positive and negative directions of vec,
        or only the positive.

        Args:
            p: tested point
            vec: projection vector
            fwd_only: if True, only the forward (positive) direction of vec is considered

        Return:
            True if the projected point hits the surface
        """
        # Get coefficients of the plane equation
        a, b, c, d = self.plane_equation_coefficients()

        # Find the point projection alogn vec to the plane of the polygon
        denom = (a * vec[0] + b * vec[1] + c * vec[2])

        if np.abs(denom) < GEOM_EPSILON:
            # Vector vec is perpendicular to the plane
            return False
        else:
            # Projection crosses the surface of the plane
            s = (-d - a * p.x - b * p.y - c * p.z) / (a * vec[0] + b * vec[1] + c * vec[2])

            if fwd_only and s < 0:
                # The plane is in the other direction than the one pointed by vec
                return False

            p = p.copy()
            p += s * vec
            is_inside = self.is_point_inside(p)
            return is_inside

    def is_point_behind(self, p: Point) -> bool:
        """Checks if the point p is behind the polygon.

        A point is behind the polygon if the polygon's normal vector
        is directed in the opposite direction to the point.
        """
        # Translate polygon's to the point p
        _, _, _, d = self.plane_equation_coefficients()
        _, _, _, dp = self.projection_coefficients(p)

        # Distance
        # Negative distance -> point behind the polygon
        # Positive distance -> point in front of the polygon
        dist = d - dp

        if dist < 0:
            return True
        else:
            return False

    def _triangulate(self) -> list:
        """Return a list of triangles (i, j, k) using the ear clipping algorithm.

        (i, j, k) are the indices of the points in self.points.
        """
        return triangulate(self.points, self.normal)

    def _normal(self) -> np.ndarray:
        """Calculate a unit normal vector for this wall.

        The normal vector is calculated using the cross product
        of two vectors A and B spanning between points:
        - A: 0 -> 1 (first and second point)
        - B: 0 -> -1 (first and last point)
        """
        # TODO: use building3d.geom.vector.normal() instead
        vec_a = vector(self.points[0], self.points[1])
        vec_b = vector(self.points[0], self.points[-1])
        norm = np.cross(vec_a, vec_b)

        len_norm = length(norm)
        if len_norm < GEOM_EPSILON:
            raise GeometryError("Normal vector has zero length")
        else:
            norm /= len_norm

        return norm

    def _edges(self) -> list[tuple[Point, Point]]:
        """Return a list of edges of this wall."""
        wall_line_segments = []
        segment = []

        i = 0
        while i < len(self.points):
            segment.append(self.points[i])
            i += 1

            if len(segment) == 2:
                wall_line_segments.append(tuple(segment))
                segment = []
                i -= 1

        return wall_line_segments

    def _area(self):
        """Calculate the area of the wall.

        Calculated using the Stoke's theorem:
        https://en.wikipedia.org/wiki/Stokes%27_theorem

        Code based on:
        https://stackoverflow.com/questions/12642256/find-area-of-polygon-from-xyz-coordinates
        """
        poly = [(p.x, p.y, p.z) for p in self.points]

        if len(poly) < 3: # not a plane - no area
            return 0

        total = [0, 0, 0]
        N = len(poly)
        for i in range(N):
            vi1 = poly[i]
            if i == N - 1:
                vi2 = poly[0]
            else:
                vi2 = poly[i+1]
            prod = np.cross(vi1, vi2)
            total[0] += prod[0]
            total[1] += prod[1]
            total[2] += prod[2]

        result = np.dot(total, self.normal)

        return abs(result / 2)

    def _are_points_coplanar(self) -> bool:
        vec_n = self.normal

        # Plane equation:
        # ax + by + cz + d = 0
        # (a, b, c) are taken from the normal vector
        # d is calculated by substituting one of the points
        ref = 0  # reference point index
        ref_pt = self.points[ref]
        d = -1 * (vec_n[0] * ref_pt.x + vec_n[1] * ref_pt.y + vec_n[2] * ref_pt.z)

        # Check if all points lay on the same plane
        for pt in self.points:
            coplanar = np.abs(vec_n[0] * pt.x + vec_n[1] * pt.y + vec_n[2] * pt.z + d) < GEOM_EPSILON
            if not coplanar:
                return False
        return True

    def _verify(self):
        """Verify geometry correctness."""
        # At least 3 points
        if len(self.points) < 3:
            raise GeometryError(f"Polygon has only {len(self.points)} points")

        # Check if all points are coplanar
        if not self._are_points_coplanar():
            raise GeometryError(f"Points of polygon aren't coplanar")

    def _centroid(self) -> Point:
        """Calculate the center of mass.

        The centroid is calculated using a weighted average of
        the triangle centroids. The weights are the triangle areas.

        Uses self.triangles (the output of self.triangulate()).
        """
        tri_ctr = []
        weights = []

        assert len(self.triangles) > 0, "No triangles after ear clipping?"

        for tri in self.triangles:
            tri_ctr.append(
                triangle_centroid(
                    self.points[tri[0]], self.points[tri[1]], self.points[tri[2]]
                )
            )
            weights.append(
                triangle_area(
                    self.points[tri[0]], self.points[tri[1]], self.points[tri[2]]
                )
            )
        tri_ctr_arr = np.array([(p.x, p.y, p.z) for p in tri_ctr])
        weights_arr = np.array(weights).reshape((-1, 1))

        weighted_centroids = tri_ctr_arr * weights_arr

        vec = weighted_centroids.sum(axis=0) / weights_arr.sum()
        ctr = Point(vec[0], vec[1], vec[2])

        return ctr

    def __del__(self):
        Polygon.remove_name(self.name)
