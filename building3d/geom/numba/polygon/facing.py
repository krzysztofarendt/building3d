from numba import njit
import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.numba.points import points_equal
from building3d.geom.numba.types import PointType, VectorType
from building3d.geom.numba.polygon.area import polygon_area
from building3d.geom.numba.points import bounding_box


@njit
def are_polygons_facing(
    pts1: PointType,
    vn1: VectorType,
    pts2: PointType,
    vn2: VectorType,
) -> bool:
    """Checks if two polygons are facing each other.

    Returns True if all points are same and their normals are pointing towards each other.

    Args:
        pts1: ...
        tri1: ...
        vn1: ...
        pts2: ...
        tri2: ...
        vn2: ...

    Return:
        True if the polygons are facing each other
    """
    if not np.allclose(vn1, -1 * vn2, rtol=GEOM_RTOL):
        return False

    bbox1 = bounding_box(pts1)
    bbox2 = bounding_box(pts2)
    if not are_bboxes_overlapping(bbox1, bbox2):
        return False

    num_matching = 0
    matched = set()

    # This does not test if the connections between points are same
    # So it tests also if the areas are the same
    # TODO: There might still be rare cases where it gives incorrect solutions
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
def are_bboxes_overlapping(bbox1, bbox2):
    if (bbox1[1] < bbox2[0]).any() or (bbox1[0] > bbox2[1]).any():
        return False
    else:
        return True
