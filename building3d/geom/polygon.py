import numpy as np

from .exceptions import GeometryError
from .point import Point
from .vector import Vector
from .triangle import triangle_centroid
from .triangle import triangle_area
from .triangle import is_point_inside


class Polygon:

    def __init__(self, points: list[Point]):
        self.points = points
        self.triangles = self._triangulate()
        self.centroid = self._centroid()

    def normal(self) -> tuple[Point, Point]:
        """Calculate a unit normal vector for this wall.

        The vector origin is at the center of weight.
        The normal vector is calculated using the cross product
        of two vectors A and B spanning between points:
        - A: 0 -> 1 (first and second point)
        - B: 0 -> -1 (first and last point)
        """
        ctr = self.centroid
        vec_a = self.points[0].vector() - self.points[1].vector()
        vec_b = self.points[0].vector() - self.points[-1].vector()
        norm = np.cross(vec_a, vec_b)
        norm /= np.sqrt(norm[0] ** 2 + norm[1] ** 2 + norm[2] ** 2)
        norm += ctr

        normal_beg = Point(x=ctr[0], y=ctr[1], z=ctr[2])
        normal_end = Point(x=norm[0], y=norm[1], z=norm[2])

        return (normal_beg, normal_end)

    def edges(self) -> list[tuple[Point, Point]]:
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

    def area(self):
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

        normal_beg, normal_end = self.normal()
        result = np.dot(total, Vector(normal_beg, normal_end).v)

        return abs(result / 2)

    def _are_points_coplanar(self) -> bool:
        vec_n = Vector(*self.normal()).v

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

    def verify(self):
        """Verify geometry correctness."""
        # At least 3 points
        if len(self.points) < 3:
            raise GeometryError(f"Wall {self.name} has only {len(self.points)} points")

        # Check if all points are coplanar
        if not self._are_points_coplanar():
            raise GeometryError(f"Points of wall {self.name} aren't coplanar")

    def _triangulate(self) -> list:
        """Return a list of triangles (i, j, k) using the ear clipping algorithm.

        (i, j, k) are the indices of the points in self.points.
        """
        def is_convex(p0, p1, p2):
            """Check if the angle between p1->p0 and p1->p2 is less than 180 degress."""
            v1 = Vector(p1, p0)
            v2 = Vector(p1, p2)
            if v1.angle(v2) < np.pi:
                return True
            else:
                return False

        vertices = [(i, p) for i, p in enumerate(self.points)]
        triangles = []
        pos = 0

        while len(vertices) > 2:

            if pos > len(vertices) - 1:
                pos = 0
            prev_pos = pos - 1 if pos > 0 else len(vertices) - 1
            next_pos = pos + 1 if pos < len(vertices) - 1 else 0

            prev_id, prev_pt = vertices[prev_pos]
            curr_id, curr_pt = vertices[pos]
            next_id, next_pt = vertices[next_pos]

            if is_convex(prev_pt, curr_pt, next_pt):
                # Check if no other point is within this triangle
                # Needed for non-convex polygons
                any_point_inside = False

                for i in range(0, len(vertices)):
                    test_id = vertices[i][0]
                    if test_id not in (prev_id, curr_id, next_id):
                        any_point_inside = is_point_inside(
                            self.points[test_id],
                            self.points[prev_id],
                            self.points[curr_id],
                            self.points[next_id],
                        )

                if not any_point_inside:
                    # Add triangle
                    triangles.append((prev_id, curr_id, next_id))

                    # Remove pos from index
                    vertices.pop(pos)

                else:
                    # Some point inside this triangle
                    # It is not an ear
                    pass

            pos += 1

        return triangles

    def _centroid(self) -> np.ndarray:
        """Calculate the center of mass.

        The centroid is calculated using a weighted average of
        the triangle centroids. The weights are the triangle areas.

        Uses self.triangles (the output of self.triangulate()).
        """
        tri_ctr = []
        weights = []

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

        return weighted_centroids.sum(axis=0) / weights_arr.sum()
