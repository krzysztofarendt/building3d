import numpy as np
import pytest

from building3d.geom.numba.types import FLOAT
from building3d.geom.numba.points import find_close_pairs


def test_find_close_pairs():
    pts1 = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
    ], dtype=FLOAT)

    pts2 = np.array([
        [0.4, 0.1, 0],
        [0.9, 0.1, 0],
        [0.9, 0.8, 0],
        [0.5, 0.3, 0],
    ], dtype=FLOAT)

    pairs = find_close_pairs(pts1, pts2, n=1)
    assert np.allclose(pairs, [[[1, 0, 0], [0.9, 0.1, 0]]])

    pairs = find_close_pairs(pts1, pts2, n=4)
    assert np.allclose(pairs, [
        [[1, 0, 0], [0.9, 0.1, 0]],
        [[1, 1, 0], [0.9, 0.8, 0]],
        [[0, 0, 0], [0.4, 0.1, 0]],
        [[0, 1, 0], [0.5, 0.3, 0]],
    ])

    with pytest.raises(ValueError):
        pairs = find_close_pairs(pts1, pts2, n=5)
