import numpy as np

from building3d.random import random_id
from building3d.config import GEOM_RTOL
from building3d.geom.exceptions import GeometryError
from building3d.geom.points import are_points_coplanar
from building3d.geom.polygon import Polygon
from building3d.geom.polygon.slice.add_intersection_points import \
    add_intersection_points
from building3d.geom.polygon.slice.get_point_arrays import get_point_arrays
from building3d.geom.polygon.slice.remove_redundant_points import \
    remove_redundant_points
from building3d.geom.types import PointType
from building3d.geom.types import VectorType


def slice_polygon(
    poly: Polygon,
    slicing_pts: PointType,
    pt1: PointType | None = None,
    name1: str | None = None,
    pt2: PointType | None = None,
    name2: str | None = None,
) -> tuple[Polygon, Polygon]:
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

    Returns:
        tuple of new polygons or Nones if slicing not possible

    Raises:
        GeometryError: if slicing not possible
    """
    assert are_points_coplanar(
        np.vstack((poly.pts, slicing_pts))
    ), "Polygon points are not coplanar with slicing points"

    _, slicing_pts = add_intersection_points(poly.pts, slicing_pts)

    slicing_pts = remove_redundant_points(slicing_pts, poly.pts, poly.tri)

    if slicing_pts.shape[0] < 2:
        # Slicing not possible
        raise GeometryError("Slicing not possible, less than 2 valid slicing points")

    pts1, pts2 = get_point_arrays(poly.pts, poly.tri, slicing_pts)
    poly1, poly2 = make_polygons(poly.vn, pts1, pts2, pt1, name1, pt2, name2)

    # Below code is generally not needed, because the normal vector is passed to
    # `make_polygon()` so poly1 and poly2 should be oriented properly,
    # but it does no harm to double check because it's cheap
    if not np.allclose(poly1.vn, poly.vn, rtol=GEOM_RTOL):
        poly1 = poly1.flip(poly1.name)
        assert np.allclose(poly1.vn, poly.vn, rtol=GEOM_RTOL)
    if not np.allclose(poly2.vn, poly.vn, rtol=GEOM_RTOL):
        poly2 = poly2.flip(poly2.name)
        assert np.allclose(poly2.vn, poly.vn, rtol=GEOM_RTOL)

    return poly1, poly2


def make_polygons(
    vn: VectorType,
    pts1: PointType,
    pts2: PointType,
    pt1: PointType | None = None,
    name1: str | None = None,
    pt2: PointType | None = None,
    name2: str | None = None,
) -> tuple[Polygon, Polygon]:
    """Get polygons from `pts1` and `pts2` and assign names.

    To assign names `name1`, `name2` at least one point (`pt1`, `pt2`) must be provided.

    Args:
        vn: normal vector of the new polygons
        pts1: points of polygon 1
        pts2: points of polygon 2
        pt1: optional point inside one of the resulting slices
        name1: optional name of part associated with pt1
        pt2: optional point inside the other one of the resulting slices
        name2: optional name of part associated with pt2

    Return:
        tuple of new polygons
    """
    # Normal vector vn is passed because we can't be sure if pts1 and pts2 start in a convex corner.
    # If the first corner is non-convex and vn is not given polygon triangulation fails.
    # Fortunately, vn is known, because it is the same as in the original polygon.
    poly1 = Polygon(pts1, vn=vn)
    poly2 = Polygon(pts2, vn=vn)

    if name1 is None:
        name1 = random_id()
    if name2 is None:
        name2 = random_id()

    if (pt1 is not None) and (pt2 is not None):
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

    elif (pt1 is not None) and (pt2 is None):
        if poly1.is_point_inside(pt1):
            poly1.name = name1
            poly2.name = name2
        elif poly2.is_point_inside(pt1):
            poly1.name = name2
            poly2.name = name1
        else:
            raise GeometryError("pt1 given but outside both polygons")

    elif (pt1 is None) and (pt2 is not None):
        if poly1.is_point_inside(pt2):
            poly1.name = name2
            poly2.name = name1
        elif poly2.is_point_inside(pt2):
            poly1.name = name1
            poly2.name = name2
        else:
            raise GeometryError("pt2 given but outside both polygons")

    else:
        poly1.name = name1
        poly2.name = name2

    if poly1.name == name1 and poly2.name == name2:
        return (poly1, poly2)
    elif poly1.name == name2 and poly2.name == name1:
        return (poly2, poly1)
    else:
        raise RuntimeError("Such a case should not happen")
