import numpy as np
from building3d.geom.types import INT, FLOAT
from building3d.simulators.rays_numba.bvh import make_bvh_grid


def test_make_bvh_grid():
    """Test written by Claude 3.5 Sonnet.

    This unit test does the following:
    1. It imports the necessary modules and the `make_bvh_grid` function.
    2. It defines a test function `test_make_bvh_grid()`.
    3. Inside the test function, it sets up test inputs including
       `min_xyz`, `max_xyz`, `poly_pts`, `poly_tri`, and `step`.
    4. It calls the `make_bvh_grid()` function with these inputs.
    5. It then asserts various expectations about the result:
       - The result should be a dictionary.
       - The grid should have 8 cells (2x2x2).
       - It checks specific grid cells to ensure they contain the expected polygons.
       - It verifies that all polygons are accounted for in the grid.
    """
    # Define test inputs
    min_xyz = (0.0, 0.0, 0.0)
    max_xyz = (2.0, 2.0, 2.0)
    poly_pts = [
        np.array(
            [(0.5, 0.5, 0.5), (1.5, 0.5, 0.5), (1.5, 1.5, 0.5), (0.5, 1.5, 0.5)],
            dtype=FLOAT,
        ),
        np.array(
            [(0.5, 0.5, 1.5), (1.5, 0.5, 1.5), (1.5, 1.5, 1.5), (0.5, 1.5, 1.5)],
            dtype=FLOAT,
        ),
    ]
    poly_tri = [
        np.array([(0, 1, 2), (0, 2, 3)], dtype=INT),
        np.array([(0, 1, 2), (0, 2, 3)], dtype=INT),
    ]
    step = 1.0

    # Call the function
    result = make_bvh_grid(min_xyz, max_xyz, poly_pts, poly_tri, step)

    # Assert the expected results
    # Cannot use isinstance(result, dict), because when njit is used,
    # the type is a numba-specific typed dict
    assert hasattr(result, 'keys') and hasattr(result, 'values'), "Result should be dict-like"
    assert len(result) == 8  # 2x2x2 grid

    # Check some specific grid cells
    assert set(result[(0, 0, 0)]) == {0}  # Lower polygon
    assert set(result[(0, 0, 1)]) == {1}  # Upper polygon
    assert set(result[(1, 1, 0)]) == {0}  # Lower polygon
    assert set(result[(1, 1, 1)]) == {1}  # Upper polygon

    # Check that all polygons are accounted for
    all_polygons = set()
    for cell_polygons in result.values():
        all_polygons.update(cell_polygons)
    assert all_polygons == {0, 1}


if __name__ == "__main__":
    test_make_bvh_grid()
