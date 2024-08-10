from numba import njit
import numpy as np

from building3d import random_id
from building3d.geom.exceptions import GeometryError
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.numba.config import PointType, VectorType, IndexType
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.vectors import normal
from building3d.geom.numba.triangles import triangulate
from building3d.geom.numba.triangles import triangle_centroid
from building3d.geom.numba.triangles import triangle_area
from building3d.geom.numba.config import FLOAT


class Polygon:
    def __init__(
        self,
        points: PointType,
        name: str | None = None,
        uid: str | None = None,
        triangles: IndexType | None = None,
    ):
        if name is None:
            name = random_id()
        self.name: str = validate_name(name)

        self.uid: str = ""
        if uid is None:
            self.uid = random_id()
        else:
            self.uid = uid

        self.points: PointType = points
        self.normal: VectorType = normal(self.points[-1], self.points[0], self.points[1])

        if triangles is None:
            self.triangles = triangulate(self.points, self.normal)
        else:
            assert len(triangles) > 0, "Empty triangles provided"
            self.triangles: IndexType = triangles

    def _verify(self):
        # Check if at least 3 points
        num_points = self.points.shape[0]
        if num_points < 3:
            raise GeometryError(f"Polygon needs at least 3 points. {num_points} were given.")

        # Check if points are coplanar
        if not are_points_coplanar(self.points):
            raise GeometryError("Polygon points must be coplanar.")


@njit
def polygon_centroid(pts: PointType, tri: IndexType) -> PointType:
    """Calculate the center of mass.

    The centroid is calculated using a weighted average of
    the triangle centroids. The weights are the triangle areas.

    Uses self.triangles (the output of self.triangulate()).
    """
    num_tri = tri.shape[0]
    assert num_tri > 0, "No triangles passed"

    tri_ctr = np.zeros((num_tri, 3), dtype=FLOAT)
    weights = np.zeros(num_tri, dtype=FLOAT)

    for i in range(num_tri):
        tri_ctr[i] = triangle_centroid(pts[tri[i, 0]], pts[tri[i, 1]], pts[tri[i, 2]])
        weights[i] = triangle_area(pts[tri[i, 0]], pts[tri[i, 1]], pts[tri[i, 2]])

    poly_ctr = np.zeros(3, dtype=FLOAT)
    for i in range(num_tri):
        poly_ctr += tri_ctr[i] * weights[i]

    return poly_ctr
