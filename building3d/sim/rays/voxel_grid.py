import numpy as np
from numba import njit

from building3d.geom.types import INT
from building3d.geom.types import IndexType
from building3d.geom.types import PointType

from .jit_print import jit_print


@njit
def make_voxel_grid(
    min_xyz: tuple[float, float, float],
    max_xyz: tuple[float, float, float],
    poly_pts: list[PointType],
    step: float = 1.0,
    eps: float = 1e-4,
    verbose: bool = True,
) -> dict[tuple[int, int, int], IndexType]:
    """Create a voxel grid for faster collision detection.

    This function divides the space defined by min_xyz and max_xyz into a grid of cubes,
    and associates each polygon with the grid cells it intersects or is contained within.

    Args:
        min_xyz (tuple[float, float, float]): Minimum coordinates (x, y, z) of the bounding box.
        max_xyz (tuple[float, float, float]): Maximum coordinates (x, y, z) of the bounding box.
        poly_pts (list[PointType]): List of points for each polygon.
        step (float, optional): Size of each grid cell. Defaults to 1.0.
        eps (float, optional): Small number used in comparison operations.
        verbose (bool, optional): Prints progress if True

    Returns:
        dict[tuple[int, int, int], IndexType]: A dictionary where keys are grid
        cell coordinates and values are sets of polygon indices that intersect
        with or are contained within each cell
    """
    min_x, min_y, min_z = min_xyz
    max_x, max_y, max_z = max_xyz

    min_x -= eps
    min_y -= eps
    min_z -= eps
    max_x += eps
    max_y += eps
    max_z += eps

    grid = {}

    # The range is extended with "+step" to accommodate models
    # with negative and positive coordinates
    x_range = np.arange(min_x, max_x + step + eps, step)
    y_range = np.arange(min_y, max_y + step + eps, step)
    z_range = np.arange(min_z, max_z + step + eps, step)

    keys = []
    for x in x_range:
        for y in y_range:
            for z in z_range:
                keys.append(
                    (
                        int(np.floor(x / step)),
                        int(np.floor(y / step)),
                        int(np.floor(z / step)),
                    )
                )

    max_polygons_per_cell = len(poly_pts)  # Worst case: all polygons in one cell
    added_polygons = np.zeros(len(poly_pts), dtype=np.bool_)

    # TODO: https://github.com/krzysztofarendt/building3d/issues/73
    #       Cannot use numba.prange() due to error "double free or corruption (!prev)"
    #       I don't know what causes this error. It happens only fromt time to time.
    #       Anyway, this function is now pretty fast, so it is not needed.
    jit_print(verbose, "Total number of voxels:", len(keys))
    for ki in range(len(keys)):
        if ki % 100 == 0:
            jit_print(verbose, "Current voxel:", ki, "/", len(keys))
        key = keys[ki]
        polynums = np.full(max_polygons_per_cell, -1, dtype=INT)
        counter = 0
        for pn, pts in enumerate(poly_pts):
            min_xyz_cube = (key[0] * step, key[1] * step, key[2] * step)
            max_xyz_cube = (
                min_xyz_cube[0] + step,
                min_xyz_cube[1] + step,
                min_xyz_cube[2] + step,
            )
            outside = False
            for xyz in range(3):
                # Check if it is possible for this triangle to cross the polygon
                if (pts[:, xyz] < min_xyz_cube[xyz]).all():
                    outside = True
                    break
                if (pts[:, xyz] > max_xyz_cube[xyz]).all():
                    outside = True
                    break
            if outside:
                continue
            else:
                # Previously I had here is_polygon_crossing_cube() but it was redundant
                polynums[counter] = pn
                counter += 1
                added_polygons[pn] = True
        grid[key] = polynums[:counter]  # Only keep the valid polygon numbers

    if not np.all(added_polygons):
        raise ValueError("Not all polygons added to the voxel grid")

    jit_print(verbose, "Voxels created")
    return grid
