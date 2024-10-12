from numba import njit
import numpy as np

from building3d.geom.types import FLOAT, INT, PointType, IndexType
from building3d.geom.polygon.crossing import is_line_segment_crossing_polygon


# TODO: Add unit test!
# TODO: Rename to simply "grid", because it is not a tree-like structure
@njit
def make_bvh_grid(
    min_xyz: tuple[float, float, float],
    max_xyz: tuple[float, float, float],
    poly_pts: list[PointType],
    poly_tri: list[IndexType],
    step: float = 1.0,
    eps: float = 1e-6,
) -> dict[tuple[int, int, int], IndexType]:
    """Create a Bounding Volume Hierarchy (BVH) grid for faster collision detection.

    This function divides the space defined by min_xyz and max_xyz into a grid of cubes,
    and associates each polygon with the grid cells it intersects or is contained within.

    Args:
        min_xyz (tuple[float, float, float]): Minimum coordinates (x, y, z) of the bounding box.
        max_xyz (tuple[float, float, float]): Maximum coordinates (x, y, z) of the bounding box.
        poly_pts (list[PointType]): List of points for each polygon.
        poly_tri (list[IndexType]): List of triangle indices for each polygon.
        step (float, optional): Size of each grid cell. Defaults to 1.0.

    Returns:
        dict[tuple[int, int, int], IndexType]: A dictionary where keys are grid
        cell coordinates and values are sets of polygon indices that intersect
        with or are contained within each cell
    """
    min_x, min_y, min_z = min_xyz
    max_x, max_y, max_z = max_xyz
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
                keys.append((
                    int(np.floor(x / step)),
                    int(np.floor(y / step)),
                    int(np.floor(z / step)),
                ))

    # Set of polygons included in the grid - used for a sanity check
    used_polygons = set()

    # TODO: This loop could be parallelized with numba.prange()
    for key in keys:
        # TODO: replace grid values with sets once Numba supports them as values of typed dicts
        #       https://numba.pydata.org/numba-doc/dev/reference/pysupported.html#typed-dict
        polynums = []
        for pn, (pts, tri) in enumerate(zip(poly_pts, poly_tri)):
            min_xyz_cube = (key[0] * step, key[1] * step, key[2] * step)
            max_xyz_cube = (
                min_xyz_cube[0] + step,
                min_xyz_cube[1] + step,
                min_xyz_cube[2] + step,
            )
            if is_polygon_crossing_cube(pts, tri, min_xyz_cube, max_xyz_cube):
                polynums.append(pn)
                used_polygons.add(pn)
        grid[key] = np.array(polynums, dtype=INT)

    assert len(used_polygons) == len(poly_pts), "Not all polygons included in the grid."

    return grid


@njit
def is_polygon_crossing_cube(
    pts,
    tri,
    min_xyz,
    max_xyz,
    eps: float = 1e-6
) -> bool:
    """Check if a polygon intersects with or is contained within a cube.

    Args:
        pts: List of points representing the polygon vertices.
        tri: List of triangle indices defining the polygon's triangulation.
        min_xyz (tuple): Minimum coordinates (x, y, z) of the cube.
        max_xyz (tuple): Maximum coordinates (x, y, z) of the cube.
        eps (float): Small number for comparison operations.

    Returns:
        bool: True if the polygon intersects with or is contained within the cube, False otherwise.
    """
    # Check if any polygon vertex is inside the cube
    for pt in pts:
        x, y, z = pt
        max_x, max_y, max_z = max_xyz
        min_x, min_y, min_z = min_xyz

        if (
            min_x - eps < x < max_x + eps and
            min_y - eps < y < max_y + eps and
            min_z - eps < z < max_z + eps
        ):
            return True

    # Check if any of the cube edges crosses the polygon
    edges = cube_edges(min_xyz, max_xyz)

    for i in range(len(edges)):
        seg_start = edges[i, 0]
        seg_end = edges[i, 1]
        if is_line_segment_crossing_polygon(seg_start, seg_end, pts, tri):
            return True

    return False


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
    edges = np.array((
        ((p0[0], p0[1], p0[2]), (p1[0], p0[1], p0[2])),  # Bottom front
        ((p0[0], p0[1], p0[2]), (p0[0], p1[1], p0[2])),  # Bottom left
        ((p0[0], p0[1], p0[2]), (p0[0], p0[1], p1[2])),  # Front left
        ((p1[0], p0[1], p0[2]), (p1[0], p1[1], p0[2])),  # Bottom right
        ((p1[0], p0[1], p0[2]), (p1[0], p0[1], p1[2])),  # Front right
        ((p0[0], p1[1], p0[2]), (p1[0], p1[1], p0[2])),  # Bottom back
        ((p0[0], p1[1], p0[2]), (p0[0], p1[1], p1[2])),  # Back left
        ((p0[0], p0[1], p1[2]), (p1[0], p0[1], p1[2])),  # Top front
        ((p0[0], p0[1], p1[2]), (p0[0], p1[1], p1[2])),  # Top left
        ((p1[0], p1[1], p0[2]), (p1[0], p1[1], p1[2])),  # Back right
        ((p1[0], p0[1], p1[2]), (p1[0], p1[1], p1[2])),  # Top right
        ((p0[0], p1[1], p1[2]), (p1[0], p1[1], p1[2])),  # Top back
    ))
    return edges
