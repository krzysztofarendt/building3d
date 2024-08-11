from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.numba.types import PointType, VectorType, IndexType
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.vectors import normal
from building3d.geom.numba.triangles import triangulate
from building3d.geom.numba.polygon.centroid import polygon_centroid


class Polygon:
    def __init__(
        self,
        points: PointType,
        name: str | None = None,
        uid: str | None = None,
        triangles: IndexType | None = None,
    ):
        # Sanity checks
        assert are_points_coplanar(points), "Polygon points must be coplanar"
        assert len(points) >= 3, "Polygon needs at least 3 points"

        # Attribute assignment
        if name is None:
            name = random_id()
        self.name: str = validate_name(name)

        self.uid: str = ""
        if uid is None:
            self.uid = random_id()
        else:
            self.uid = uid

        self.pts: PointType = points
        self.vn: VectorType = normal(self.pts[-1], self.pts[0], self.pts[1])

        if triangles is None:
            self.tri: IndexType = triangulate(self.pts, self.vn)
        else:
            assert len(triangles) > 0, "Empty triangles provided"
            self.tri: IndexType = triangles

        self.ctr = polygon_centroid(self.pts, self.tri)
