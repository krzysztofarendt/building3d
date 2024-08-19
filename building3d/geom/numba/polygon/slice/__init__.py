import numpy as np

from building3d.geom.exceptions import GeometryError
from building3d.geom.numba.types import PointType
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.slice.get_point_arrays import get_point_arrays
from building3d.geom.numba.polygon.slice.add_intersection_points import add_intersection_points
from building3d.geom.numba.polygon.slice.remove_redundant_points import remove_redundant_points


def slice_polygon(
    poly: Polygon,
    slicing_pts: PointType,
    pt1: PointType | None = None,
    name1: str | None = None,
    pt2: PointType | None = None,
    name2: str | None = None,
) -> tuple[Polygon, Polygon] | tuple[None, None]:
    """Slice polygon into two parts.

    To assign names, all optional arguments needs to be provided.

    NOTE:
        Slicing points must divide the polygon into exactly 2 parts.

    Args:
        poly: polygon instrance
        slicing_pts: slicing points
        pt1: optional point inside one of the resulting slices
        name1: optional name of part associated with pt1
        pt2: optional point inside the other one of the resulting slices
        name2: optional name of part associated with pt2

    Return:
        tuple of new polygons or Nones if slicing not possible
    """
    assert are_points_coplanar(np.vstack((poly.pts, slicing_pts))), \
        "Polygon points are not coplanar with slicing points"

    _,  slicing_pts = add_intersection_points(poly.pts, slicing_pts)

    slicing_pts = remove_redundant_points(slicing_pts, poly.pts, poly.tri)

    if slicing_pts.shape[0] < 2:
        # Slicing not possible
        return None, None  # TODO: I don't like it

    pts1, pts2 = get_point_arrays(poly.pts, poly.tri, slicing_pts)
    poly1, poly2 = make_polygons(pts1, pts2, pt1, name1, pt2, name2)

    return poly1, poly2


def make_polygons(
    pts1: PointType,
    pts2: PointType,
    pt1: PointType | None = None,
    name1: str | None = None,
    pt2: PointType | None = None,
    name2: str | None = None,
) -> tuple[Polygon, Polygon]:
    """Get polygons from `pts1` and `pts2` and assign names.

    To assign names, all optional arguments needs to be provided.

    Args:
        poly: polygon instrance
        slicing_pts: slicing points
        pt1: optional point inside one of the resulting slices
        name1: optional name of part associated with pt1
        pt2: optional point inside the other one of the resulting slices
        name2: optional name of part associated with pt2

    Return:
        tuple of new polygons
    """
    poly1 = Polygon(pts1)
    poly2 = Polygon(pts2)

    if (
        pt1 is not None and
        name1 is not None and
        pt2 is not None and
        name2 is not None
    ):
        if poly1.is_point_inside(pt1):
            poly1.name = name1
        elif poly1.is_point_inside(pt2):
            poly1.name = name2
        else:
            raise GeometryError("None of the points is inside polygon made of pts1")

        if poly2.is_point_inside(pt1):
            poly2.name = name1
        elif poly2.is_point_inside(pt2):
            poly2.name = name2
        else:
            raise GeometryError("None of the points is inside polygon made of pts2")

    return (poly1, poly2)
