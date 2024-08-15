import logging

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.numba.types import PointType, VectorType, IndexType, FLOAT
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.vectors import normal
from building3d.geom.numba.triangles import triangulate
from building3d.geom.numba.triangles import triangle_centroid
from building3d.geom.numba.polygon.centroid import polygon_centroid
from building3d.geom.numba.polygon.area import polygon_area
from building3d.geom.numba.polygon.plane import plane_coefficients
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.polygon.polygonsfacing import are_polygons_facing


logger = logging.getLogger(__name__)


class Polygon:
    def __init__(
        self,
        pts: PointType,
        name: str | None = None,
        uid: str | None = None,
        tri: IndexType | None = None,
    ):
        # Sanity checks
        assert are_points_coplanar(pts), "Polygon points must be coplanar"
        assert len(pts) >= 3, "Polygon needs at least 3 points"

        # Attribute assignment
        if name is None:
            name = random_id()
        self.name: str = validate_name(name)

        self.uid: str = ""
        if uid is None:
            self.uid = random_id()
        else:
            self.uid = uid

        self.pts: PointType = pts
        self.vn: VectorType = normal(self.pts[-1], self.pts[0], self.pts[1])

        if tri is None:
            self.tri: IndexType = triangulate(self.pts, self.vn)
        else:
            assert len(tri) > 0, "Empty triangles provided"
            self.tri: IndexType = tri

        self.ctr: PointType = polygon_centroid(self.pts, self.tri)
        self.area: float = polygon_area(self.pts, self.vn)
        self.plane_coefficients: tuple[FLOAT, FLOAT, FLOAT, FLOAT] = plane_coefficients(self.pts)

    def get_mesh(self) -> tuple[PointType, IndexType]:
        """Get vertices and faces of this polygon.

        This function returns faces generated by the ear-clipping algorithm.

        Return:
            tuple of vertices, shaped (num_pts, 3), and faces, shaped (num_tri, 3)
        """
        return self.pts, self.tri

    def flip(self, new_name: str | None = None):
        """Copies and flips the polygon. Changes the name.

        Args:
            new_name: polygon name (must be unique within a Wall)

        Returns:
            Polygon
        """
        return Polygon(self.pts[::-1].copy(), name=new_name)

    def get_some_interior_point(self) -> PointType:
        """Return some point laying inside this polygon.

        Such point is sometimes needed to distuingish inside from outside.
        """
        pt1 = self.pts[self.tri[0, 0]]
        pt2 = self.pts[self.tri[0, 1]]
        pt3 = self.pts[self.tri[0, 2]]
        some_pt = triangle_centroid(pt1, pt2, pt3)
        return some_pt

    def is_point_inside(self, pt: PointType) -> bool:
        return is_point_inside(pt, self.pts, self.tri)

    def is_facing_polygon(self, other, exact: bool = True) -> bool:
        return are_polygons_facing(
            self.pts, self.tri, self.vn, other.pts, other.tri, other.vn, exact
        )

    def __str__(self):
        return f"Polygon(name={self.name}, points={self.pts}, id={hex(id(self))})"

    def __repr__(self):
        return self.__str__()
