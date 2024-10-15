from numba import njit, prange
import numpy as np

from building3d.geom.types import FLOAT, INT, PointType, IndexType
from building3d.geom.polygon.crossing import is_line_segment_crossing_polygon


# TODO: Add unit test!
@njit(parallel=True)
def make_voxel_grid(
    min_xyz: tuple[float, float, float],
    max_xyz: tuple[float, float, float],
    poly_pts: list[PointType],
    poly_tri: list[IndexType],
    step: float = 1.0,
    eps: float = 1e-4,
) -> dict[tuple[int, int, int], IndexType]:
    """Create a voxel grid for faster collision detection.

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

    for ki in prange(len(keys)):
        key = keys[ki]
        polynums = np.full(max_polygons_per_cell, -1, dtype=INT)
        counter = 0
        for pn, (pts, tri) in enumerate(zip(poly_pts, poly_tri)):
            min_xyz_cube = (key[0] * step, key[1] * step, key[2] * step)
            max_xyz_cube = (
                min_xyz_cube[0] + step,
                min_xyz_cube[1] + step,
                min_xyz_cube[2] + step,
            )
            if is_polygon_crossing_cube(pts, tri, min_xyz_cube, max_xyz_cube):
                polynums[counter] = pn
                counter += 1
                added_polygons[pn] = True
        grid[key] = polynums[:counter]  # Only keep the valid polygon numbers

    assert np.all(added_polygons), "Not all polygons added to the voxel grid"

    return grid


@njit
def is_polygon_crossing_cube(pts, tri, min_xyz, max_xyz, eps: float = 1e-3) -> bool:
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
            min_x - eps <= x <= max_x + eps
            and min_y - eps <= y <= max_y + eps
            and min_z - eps <= z <= max_z + eps
        ):
            return True

    # Check if any of the polygon edges intersects with the cube
    cube_faces = cube_polygons(min_xyz, max_xyz)
    for i in range(len(tri)):
        for j in range(3):  # Check all three edges of each triangle
            edge_start = pts[tri[i][j]]
            edge_end = pts[tri[i][(j + 1) % 3]]
            for face in cube_faces:
                if is_line_segment_crossing_polygon(
                    edge_start,
                    edge_end,
                    face,
                    np.array([[0, 1, 2], [0, 2, 3]], dtype=INT),
                ):
                    return True

    # Check if any of the cube edges crosses the polygon
    edges = cube_edges(min_xyz, max_xyz)
    for edge in edges:
        seg_start, seg_end = edge
        if is_line_segment_crossing_polygon(seg_start, seg_end, pts, tri, 1e-10):
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
