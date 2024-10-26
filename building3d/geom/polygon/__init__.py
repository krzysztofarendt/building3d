import logging

import numpy as np

from building3d import random_id
from building3d.config import GEOM_ATOL
from building3d.geom.paths import PATH_SEP
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.points import are_points_coplanar
from building3d.geom.bboxes import bounding_box
from building3d.geom.polygon.area import polygon_area
from building3d.geom.polygon.centroid import polygon_centroid
from building3d.geom.polygon.crossing import are_polygons_crossing
from building3d.geom.polygon.facing import are_polygons_facing
from building3d.geom.polygon.ispointinside import is_point_inside
from building3d.geom.polygon.ispointinside import is_point_inside_margin
from building3d.geom.polygon.plane import plane_coefficients
from building3d.geom.polygon.touching import are_polygons_touching
from building3d.geom.triangles import triangle_centroid
from building3d.geom.triangles import triangulate
from building3d.geom.types import FLOAT
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.types import VectorType
from building3d.geom.vectors import normal

logger = logging.getLogger(__name__)


class Polygon:
    """Polygon represents an area defined by a collection of sequentially connected points.

    NOTE:
    Polygon's normal vector is calculated using the first corner from `pts`,
    i.e. using points with index -1, 0, and 1. If the first corner is
    non-convex, the normal will be wrong and triangulation will fail. the first
    corner can be non-convex only if the normal vector is provided (argument
    `vn`). in such a case the points are rolled forward until the first corner
    is convex.
    """

    def __init__(
        self,
        pts: PointType,
        name: str | None = None,
        uid: str | None = None,
        tri: IndexType | None = None,
        vn: VectorType | None = None,
        parent=None,
    ):
        # Sanity checks
        assert are_points_coplanar(pts), "Polygon points must be coplanar"
        assert len(pts) >= 3, "Polygon needs at least 3 points"

        self._parent = parent
        self.num: None | int = None  # Used as a counter in the array format

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

        # Normal vector is calculated using the first corner from `pts`
        # If the first corner is non-convex, the normal will be wrong and triangulation will fail.
        # The first corner can be non-convex only if the normal vector is provided (argument `vn`).
        # In such a case the points are rolled forward until the first corner is convex.
        if vn is None:
            self.vn: VectorType = normal(self.pts[-1], self.pts[0], self.pts[1])
        else:
            self.vn = vn

        if tri is None:
            self.pts, self.tri = triangulate(self.pts, self.vn)
        else:
            assert len(tri) > 0, "Empty triangles provided"
            self.tri: IndexType = tri

        self.ctr: PointType = polygon_centroid(self.pts, self.tri)
        self.area: float = polygon_area(self.pts, self.vn)
        self.plane_coefficients: tuple[FLOAT, FLOAT, FLOAT, FLOAT] = plane_coefficients(
            self.pts
        )

    @property
    def children(self) -> PointType:
        return self.pts

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, wall):
        self._parent = wall

    @property
    def path(self) -> str:
        if self.parent is not None:
            p = PATH_SEP.join([self.parent.path, self.name])
            return p
        else:
            return self.name

    def bbox(self) -> tuple[PointType, PointType]:
        return bounding_box(self.pts)

    def get(self, abspath: str):
        """Get object by the absolute path."""
        obj = self
        while obj.parent is not None:
            obj = obj.parent
        building = obj
        return building.get(abspath)

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

    def is_point_inside(self, pt: PointType, boundary_in: bool = True) -> bool:
        return is_point_inside(pt, self.pts, self.tri, boundary_in)

    def contains_polygon(self, other) -> bool:
        """Checks if the other polygon is completely inside this one."""
        for pt in other.pts:
            if not is_point_inside_margin(pt, GEOM_ATOL, self.pts, self.tri):
                return False
        return True

    def is_facing_polygon(self, other) -> bool:
        """Checks is the polygon is facing another one. Compares points and normals."""
        return are_polygons_facing(self.pts, self.vn, other.pts, other.vn)

    def is_crossing_polygon(self, other) -> bool:
        """Checks if the polygon crosses (overlaps) with another one."""
        return are_polygons_crossing(self.pts, self.tri, other.pts, other.tri)

    def is_touching_polygon(self, other) -> bool:
        """Checks if the polygon touches (but doesn't cross) another one."""
        return are_polygons_touching(self.pts, self.tri, other.pts, other.tri)

    def __eq__(self, other):
        if np.allclose(self.pts, other.pts):
            return True
        else:
            return False

    def __str__(self):
        return (
            f"Polygon(name={self.name}, pts.shape={self.pts.shape}, id={hex(id(self))})"
        )

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key) -> PointType:
        return self.pts[key]
