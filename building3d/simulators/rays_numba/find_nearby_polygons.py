from numba import njit

from building3d.geom.types import IndexType


@njit
def find_nearby_polygons(
    x: int,
    y:int,
    z: int,
    grid: dict[tuple[int, int, int], IndexType],
) -> set[int]:
    """Find local polygons based on the BVH grid and location (x, y, z).

    Looks at the current cell and adjacent cells.

    Args:
        x: cell index 0,
        y: cell index 1,
        z: cell index 2,
        grid: dict with keys like (x, y, z) and arrays with polygon indices as values

    Return:
        set of polygon indices
    """
    nearby_indices = set()
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            for k in range(-1, 2, 1):
                if (x + i, y + j, z + k) in grid:
                    poly_indices = grid[(x + i, y + j, z + k)]
                    for index in poly_indices:
                        nearby_indices.add(index)
    return nearby_indices
