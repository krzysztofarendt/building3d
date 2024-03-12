import numpy as np

from .exceptions import GeometryError
from .point import Point
from .vector import vector
from .vector import length
from .triangle import triangle_centroid
from .triangle import triangle_area
from .triangle import is_point_inside as is_point_inside_triangle
from .triangle import triangulate


class Polygon:
    """Polygon defined by its vertices (Point instances).

    Notes:
    - The first point must lay in the convex corner!
    - If used as a wall, the points should be ordered counter-clockwise w.r.t.
      to the zone that this wall belongs to.
    """

    def __init__(self, points: list[Point]):
        self.points = points
        self.normal = self._normal()
        self._verify()
        self.triangles = self._triangulate()
        self.centroid = self._centroid()
        self.edges = self._edges()
        self.area = self._area()

    def is_point_coplanar(self, p: Point) -> bool:
        """Checks whether the point p is coplanar with the polygon."""
        # Temporarily add the test point to self.points
        self.points.append(p)
        is_coplanar = self._are_points_coplanar()
        # Remove the test point from self.points
        self.points = self.points[:-1]

        return is_coplanar

    def is_point_inside(self, p: Point) -> bool:
        """Checks wheter a point lies on the surface of the polygon."""


        if not self.is_point_coplanar(p):
            return False

        for triangle_indices in self.triangles:
            tri = [self.points[i] for i in triangle_indices]

            if is_point_inside_triangle(p, tri[0], tri[1], tri[2]):
                return True

        return False

    def _triangulate(self) -> list:
        """Return a list of triangles (i, j, k) using the ear clipping algorithm.

        (i, j, k) are the indices of the points in self.points.
        """
        return triangulate(self.points, self.normal)

    def _normal(self) -> np.ndarray:
        """Calculate a unit normal vector for this wall.

        The vector origin is at the center of weight.
        The normal vector is calculated using the cross product
        of two vectors A and B spanning between points:
        - A: 0 -> 1 (first and second point)
        - B: 0 -> -1 (first and last point)
        """
        vec_a = vector(self.points[0], self.points[1])
        vec_b = vector(self.points[0], self.points[-1])
        norm = np.cross(vec_a, vec_b)

        eps = 1e-6
        len_norm = length(norm)
        if len_norm < eps:
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
        eps = 1e-6
        for pt in self.points:
            coplanar = np.abs(vec_n[0] * pt.x + vec_n[1] * pt.y + vec_n[2] * pt.z + d) < eps
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
