from numba import njit
import numpy as np

from building3d.io.arrayformat import get_polygon_points_and_faces
from building3d.geom.types import PointType, VectorType, IndexType, IntDataType, FLOAT, INT


@njit
def find_target_surface(
    # Rays
    pos: PointType,
    direction: VectorType,
    # Building
    poly_pts: list[PointType],
    poly_tri: list[IndexType],
    walls: IndexType,
    solids: IndexType,
    zones: IndexType,
    # Other
    transparent_polygons: set[int],
    polygons_to_check: set[int],
) -> int:
    """...
    """
    # breakpoint()
    return 0
