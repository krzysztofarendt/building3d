import numpy as np
from numba import njit

from building3d.config import GEOM_RTOL
from building3d.geom.points import bounding_box
from building3d.geom.points import points_equal
from building3d.geom.polygon.area import polygon_area
from building3d.geom.types import PointType
from building3d.geom.types import VectorType


@njit
def are_polygons_facing(
    pts1: PointType,
    vn1: VectorType,
    pts2: PointType,
    vn2: VectorType,
) -> bool:
    """Check if two polygons are facing each other.

    This function determines if two polygons are facing each other by comparing
    their points and normal vectors. It returns True if all points are the same
    and their normals are pointing towards each other.

    Args:
        pts1 (PointType): Points of the first polygon.
        vn1 (VectorType): Normal vector of the first polygon.
        pts2 (PointType): Points of the second polygon.
        vn2 (VectorType): Normal vector of the second polygon.

    Returns:
        bool: True if the polygons are facing each other, False otherwise.

    Note:
        This function uses bounding box overlap and point matching to determine
        if polygons are facing. It may have rare cases of incorrect solutions.
    """
    if not np.allclose(vn1, -1 * vn2, rtol=GEOM_RTOL):
        return False

    bbox1 = bounding_box(pts1)
    bbox2 = bounding_box(pts2)
    if not are_bboxes_overlapping(bbox1, bbox2):
        return False

    num_matching = 0
    matched = set()

    # This does not test if the connections between points are same,
    # so it additionally tests if the areas are the same.
    # If all the points are the same and areas are the same, the polygons are
    # most likely with the same shape.
    # TODO: There might still be rare cases where it gives incorrect result.
    for i in range(pts1.shape[0]):
        for j in range(pts2.shape[0]):
            if j not in matched:
                if points_equal(pts1[i], pts2[j]):
                    num_matching += 1
                    matched.add(j)
                    break
    if num_matching == len(pts1):
        if np.isclose(polygon_area(pts1, vn1), polygon_area(pts2, vn2)):
            return True
    return False


@njit
def are_bboxes_overlapping(
    bbox1: tuple[PointType, PointType],
    bbox2: tuple[PointType, PointType],
) -> bool:
    """Check if two bounding boxes are overlapping.

    This function determines if two axis-aligned bounding boxes are overlapping
    in any dimension.

    Args:
        bbox1 (tuple of points): First bounding box, represented as
                                 [[min_x, min_y, min_z], [max_x, max_y, max_z]].
        bbox2 (tuple of points): Second bounding box, represented as
                                 [[min_x, min_y, min_z], [max_x, max_y, max_z]].

    Returns:
        bool: True if the bounding boxes overlap, False otherwise.
    """
    if (bbox1[1] < bbox2[0]).any() or (bbox1[0] > bbox2[1]).any():
        return False
    else:
        return True
