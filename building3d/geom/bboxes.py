import numpy as np
from numba import njit

from building3d.config import GEOM_ATOL
from building3d.geom.types import PointType, FLOAT


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
    # Check if max1 < min2 or min1 > max2
    if (bbox1[1] < bbox2[0]).any() or (bbox1[0] > bbox2[1]).any():
        return False
    else:
        return True


@njit
def cube_edges(
    min_xyz: tuple[FLOAT, FLOAT, FLOAT],
    max_xyz: tuple[FLOAT, FLOAT, FLOAT],
) -> PointType:
    """Generate the edges of a cube defined by its minimum and maximum coordinates.

    Args:
        min_xyz (tuple[FLOAT, FLOAT, FLOAT]): The minimum x, y, z coordinates of the cube.
        max_xyz (tuple[FLOAT, FLOAT, FLOAT]): The maximum x, y, z coordinates of the cube.

    Returns:
        Array containing 12 edges of the cube, where each edge is represented
        as two points (start_point, end_point), and each point has
        three coordinates (x, y, z). Shape = (12, 2, 3).
    """
    p0 = min_xyz
    p1 = max_xyz
    edges = np.array(
        (
            # Bottom face
            ((p0[0], p0[1], p0[2]), (p1[0], p0[1], p0[2])),  # Bottom front
            ((p0[0], p0[1], p0[2]), (p0[0], p1[1], p0[2])),  # Bottom left
            ((p0[0], p1[1], p0[2]), (p1[0], p1[1], p0[2])),  # Bottom back
            ((p1[0], p0[1], p0[2]), (p1[0], p1[1], p0[2])),  # Bottom right
            # Top face
            ((p0[0], p0[1], p1[2]), (p1[0], p0[1], p1[2])),  # Top front
            ((p0[0], p1[1], p1[2]), (p1[0], p1[1], p1[2])),  # Top back
            ((p0[0], p0[1], p1[2]), (p0[0], p1[1], p1[2])),  # Top left
            ((p1[0], p0[1], p1[2]), (p1[0], p1[1], p1[2])),  # Top right
            # Vertical edges
            ((p0[0], p0[1], p0[2]), (p0[0], p0[1], p1[2])),  # Front left vertical
            ((p1[0], p0[1], p0[2]), (p1[0], p0[1], p1[2])),  # Front right vertical
            ((p0[0], p1[1], p0[2]), (p0[0], p1[1], p1[2])),  # Back left vertical
            ((p1[0], p1[1], p0[2]), (p1[0], p1[1], p1[2])),  # Back right vertical
        )
    )
    return edges


@njit
def cube_polygons(
    min_xyz: tuple[FLOAT, FLOAT, FLOAT],
    max_xyz: tuple[FLOAT, FLOAT, FLOAT],
) -> PointType:
    """Generate the polygons of a cube defined by its minimum and maximum coordinates.

    Args:
        min_xyz (tuple[FLOAT, FLOAT, FLOAT]): The minimum x, y, z coordinates of the cube.
        max_xyz (tuple[FLOAT, FLOAT, FLOAT]): The maximum x, y, z coordinates of the cube.

    Returns:
        Array containing 6 polygons of the cube, where each polygon is represented as a list
        of four points, and each point has three coordinates (x, y, z).
    """
    p0 = min_xyz
    p1 = max_xyz
    polygons = np.array(
        [
            [  # Front polygon
                (p0[0], p0[1], p0[2]),
                (p1[0], p0[1], p0[2]),
                (p1[0], p1[1], p0[2]),
                (p0[0], p1[1], p0[2]),
            ],
            [  # Back polygon
                (p0[0], p1[1], p1[2]),
                (p1[0], p1[1], p1[2]),
                (p1[0], p0[1], p1[2]),
                (p0[0], p0[1], p1[2]),
            ],
            [  # Left polygon
                (p0[0], p0[1], p0[2]),
                (p0[0], p1[1], p0[2]),
                (p0[0], p1[1], p1[2]),
                (p0[0], p0[1], p1[2]),
            ],
            [  # Right polygon
                (p1[0], p0[1], p0[2]),
                (p1[0], p1[1], p0[2]),
                (p1[0], p1[1], p1[2]),
                (p1[0], p0[1], p1[2]),
            ],
            [  # Bottom polygon
                (p0[0], p0[1], p0[2]),
                (p1[0], p0[1], p0[2]),
                (p1[0], p0[1], p1[2]),
                (p0[0], p0[1], p1[2]),
            ],
            [  # Top polygon
                (p0[0], p1[1], p0[2]),
                (p1[0], p1[1], p0[2]),
                (p1[0], p1[1], p1[2]),
                (p0[0], p1[1], p1[2]),
            ],
        ],
        dtype=FLOAT,
    )
    return polygons
