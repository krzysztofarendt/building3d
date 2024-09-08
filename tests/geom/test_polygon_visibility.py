import numpy as np

from building3d.geom.types import FLOAT
from building3d.geom.points.visibility import visibility_matrix
from building3d.geom.polygon.edges import polygon_edges


def test_visibility_matrix():
    # L-shape
    pts = np.array(
        [
            [0, 0, 0],
            [0.5, 0, 0],
            [0.5, 0.9, 0],
            [1, 0.9, 0],
            [1, 1, 0],
            [0, 1, 0],
        ],
        dtype=FLOAT,
    )

    edges = polygon_edges(pts)

    vis = visibility_matrix(pts, edges)

    for i in range(pts.shape[0]):
        for j in range(pts.shape[0]):
            if (i, j) in ((0, 3), (3, 0), (0, 4), (4, 0), (1, 4), (4, 1)):
                assert vis[i, j] == 0
            else:
                assert vis[i, j] == 1


if __name__ == "__main__":
    test_visibility_matrix()
