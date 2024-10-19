import numpy as np
import pytest

from building3d.geom.polygon import Polygon
from building3d.geom.types import FLOAT
from building3d.sim.rays.find_target import find_target_surface



@pytest.mark.parametrize("x, y, ray_pos, ray_dir, expected_target", [
    (1.0, 1.0, [0, 0, 1], [0, 0, -1], 0),
    (2.0, 2.0, [1, 1, 2], [0, 0, -1], 0),
    (1.0, 1.0, [0.5, 0.5, 1], [0, 0, -1], 0),
    (1.0, 1.0, [0.5, 0.5, 1], [0, 0, 1], -1),
    (1.0, 1.0, [-0.01, 0, 1], [0, 0, -1], -1),
    (1.0, 0.0001, [0, 0, 1], [0, 0, -1], 0),
    (0.001, 0.001, [0, 0, 1], [0, 0, -1], 0),
    (1000, 0.00001, [1000, 0, 1], [0, 0, -1], 0),
    (0.001, 1, [0.001, 0, 1], [0, 0, -1], 0),
    # (0.0001, 1, [0.001, 0, 1], [0, 0, -1], 0),  # TODO: This one fails, insufficient precision
])
def test_find_target(x, y, ray_pos, ray_dir, expected_target):
    pts = np.array([
        [0, 0, 0],
        [x, 0, 0],
        [x, y, 0],
        [0, y, 0],
    ], dtype=FLOAT)
    poly = Polygon(pts, name="poly")
    pts, tri = poly.get_mesh()

    ray_pos = np.array(ray_pos, dtype=FLOAT)
    ray_dir = np.array(ray_dir, dtype=FLOAT)

    # Can't have an empty set because of Numba. Polygon -1 doesn't exist anyway.
    transparent = set([-1])
    polygons_to_check = set([0])

    target = find_target_surface(
        pos=ray_pos,
        direction=ray_dir,
        poly_pts=[pts],
        poly_tri=[tri],
        transparent_polygons=transparent,
        polygons_to_check=polygons_to_check,
    )

    assert target == expected_target
