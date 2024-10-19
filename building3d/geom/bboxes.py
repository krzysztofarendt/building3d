import numpy as np
from numba import njit

from building3d.geom.types import PointType, FLOAT
from building3d.config import GEOM_ATOL



@njit
def bounding_box(pts: PointType) -> tuple[PointType, PointType]:
    """Returns bounding box `((xmin, ymin, zmin), (xmax, ymax, zmax))` for points `pts`."""
    xmin, xmax = np.min(pts[:, 0]), np.max(pts[:, 0])
    ymin, ymax = np.min(pts[:, 1]), np.max(pts[:, 1])
    zmin, zmax = np.min(pts[:, 2]), np.max(pts[:, 2])
    return (
        np.array([xmin, ymin, zmin], dtype=FLOAT),
        np.array([xmax, ymax, zmax], dtype=FLOAT),
    )


@njit
def is_point_inside_bbox(
    ptest: PointType, pts: PointType, atol: float = GEOM_ATOL
) -> bool:
    """Checks whether a point is inside the bounding box for `pts`."""
    bbox = bounding_box(pts)
    if (ptest < bbox[0] - atol).any() or (ptest > bbox[1] + atol).any():
        return False
    else:
        return True


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
