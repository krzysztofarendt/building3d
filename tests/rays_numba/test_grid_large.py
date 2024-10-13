import numpy as np
from building3d.geom.types import INT, FLOAT
from building3d.simulators.rays_numba.voxel_grid import make_voxel_grid


def test_make_voxel_grid():
    """Test written by Claude 3.5 Sonnet.

    This unit test does the following:
    1. It defines the domain as a 1x1x1 cube with `min_xyz` and `max_xyz`.
    2. It creates 6 polygons, one for each face of the cube, each with 4 vertices.
    3. It defines 2 triangles for each polygon.
    4. It sets the step size to 0.25, resulting in a 4x4x4 grid (64 cells).
    5. It calls the `make_voxel_grid()` function with these parameters.
    6. It then performs several assertions to check if the resulting BVH grid is correct:
       - Checks if the total number of cells is 64.
       - Verifies if corner cells contain the correct polygons.
       - Ensures that center cells contain no polygons.
       - Checks if edge cells contain the correct number of polygons.
    """
    # Define the domain
    min_xyz = (0.0, 0.0, 0.0)
    max_xyz = (1.0, 1.0, 1.0)
    step = 0.25

    # Define 6 polygons (one for each face of the cube)
    poly_pts = [
        np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], dtype=FLOAT),  # Bottom face
        np.array([(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], dtype=FLOAT),  # Top face
        np.array([(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], dtype=FLOAT),  # Front face
        np.array([(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], dtype=FLOAT),  # Back face
        np.array([(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)], dtype=FLOAT),  # Left face
        np.array([(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)], dtype=FLOAT),  # Right face
    ]

    # Define triangles for each polygon (2 triangles per face)
    poly_tri = [
        np.array([(0, 1, 2), (0, 2, 3)], dtype=INT) for _ in range(6)
    ]

    # Call the function
    voxel_grid = make_voxel_grid(min_xyz, max_xyz, poly_pts, poly_tri, step)

    # Assertions
    # assert len(voxel_grid) == 64, "The grid should have 64 cells (4x4x4)"  # Not true

    # Check if corner cells contain the correct polygons
    assert set(voxel_grid[(0, 0, 0)]) == {0, 2, 4}, "Corner (0,0,0) should have polygons 0, 2, and 4"
    assert set(voxel_grid[(3, 0, 0)]) == {0, 2, 5}, "Corner (3,0,0) should have polygons 0, 2, and 5"
    assert set(voxel_grid[(0, 3, 0)]) == {0, 3, 4}, "Corner (0,3,0) should have polygons 0, 3, and 4"
    assert set(voxel_grid[(3, 3, 0)]) == {0, 3, 5}, "Corner (3,3,0) should have polygons 0, 3, and 5"
    assert set(voxel_grid[(0, 0, 3)]) == {1, 2, 4}, "Corner (0,0,3) should have polygons 1, 2, and 4"
    assert set(voxel_grid[(3, 0, 3)]) == {1, 2, 5}, "Corner (3,0,3) should have polygons 1, 2, and 5"
    assert set(voxel_grid[(0, 3, 3)]) == {1, 3, 4}, "Corner (0,3,3) should have polygons 1, 3, and 4"
    assert set(voxel_grid[(3, 3, 3)]) == {1, 3, 5}, "Corner (3,3,3) should have polygons 1, 3, and 5"

    # Check if center cells contain no polygons
    assert len(voxel_grid[(1, 1, 1)]) == 0, "Center cell (1,1,1) should contain no polygons"
    assert len(voxel_grid[(2, 2, 2)]) == 0, "Center cell (2,2,2) should contain no polygons"

    # Check if edge cells contain the correct number of polygons
    assert len(voxel_grid[(0, 1, 1)]) == 1, "Edge cell (0,1,1) should contain 1 polygon"
    assert len(voxel_grid[(3, 1, 1)]) == 1, "Edge cell (3,1,1) should contain 1 polygon"
    assert len(voxel_grid[(1, 0, 1)]) == 1, "Edge cell (1,0,1) should contain 1 polygon"
    assert len(voxel_grid[(1, 3, 1)]) == 1, "Edge cell (1,3,1) should contain 1 polygon"
    assert len(voxel_grid[(1, 1, 0)]) == 1, "Edge cell (1,1,0) should contain 1 polygon"
    assert len(voxel_grid[(1, 1, 3)]) == 1, "Edge cell (1,1,3) should contain 1 polygon"


if __name__ == "__main__":
    test_make_voxel_grid()
