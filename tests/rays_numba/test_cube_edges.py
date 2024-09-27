import numpy as np
import pytest

from building3d.simulators.rays_numba.bvh import cube_edges


@pytest.mark.parametrize(
    "min_xyz, max_xyz, expected_shape",
    [
        ((0, 0, 0), (1, 1, 1), (12, 2, 3)),
        ((-1, -1, -1), (1, 1, 1), (12, 2, 3)),
        ((0.5, 1.5, 2.5), (3.5, 4.5, 5.5), (12, 2, 3)),
    ],
)
def test_cube_edges(min_xyz, max_xyz, expected_shape):
    edges = cube_edges(min_xyz, max_xyz)
    assert isinstance(edges, np.ndarray)
    assert edges.shape == expected_shape

    # Check if all edges are unique
    assert len(np.unique(edges, axis=0)) == 12

    # Check if all edges connect to vertices of the cube
    vertices = [
        (min_xyz[0], min_xyz[1], min_xyz[2]),
        (min_xyz[0], min_xyz[1], max_xyz[2]),
        (min_xyz[0], max_xyz[1], min_xyz[2]),
        (min_xyz[0], max_xyz[1], max_xyz[2]),
        (max_xyz[0], min_xyz[1], min_xyz[2]),
        (max_xyz[0], min_xyz[1], max_xyz[2]),
        (max_xyz[0], max_xyz[1], min_xyz[2]),
        (max_xyz[0], max_xyz[1], max_xyz[2]),
    ]
    for edge in edges:
        assert tuple(edge[0]) in vertices
        assert tuple(edge[1]) in vertices
