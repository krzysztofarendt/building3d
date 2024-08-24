import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.numba.solid.floor_plan import floor_plan


def test_floor_plan():
    plan = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
    ]
    height = 1
    move = (0, 0, 0)
    rotate = 0

    s = floor_plan(plan, height, move, rotate)
    assert np.isclose(s.volume, 1, rtol=GEOM_RTOL)

    for w in s.children.values():
        for poly in w.get_polygons():
            assert (poly.pts >= 0).all()
            assert (poly.pts <= 1).all()


def test_floor_plan_reversed_and_moved():
    plan = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
    ]
    plan.reverse()
    height = 1
    move = (1, 1, 1)
    rotate = 0

    s = floor_plan(plan, height, move, rotate)
    assert np.isclose(s.volume, 1, rtol=GEOM_RTOL)

    for w in s.children.values():
        for poly in w.get_polygons():
            assert (poly.pts >= 1).all()
            assert (poly.pts <= 2).all()


def test_floor_plan_rotated():
    plan = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
    ]
    plan.reverse()
    height = 1
    rotate = 0.25 * np.pi

    s = floor_plan(plan, height, rot_angle=rotate)
    assert np.isclose(s.volume, 1, rtol=GEOM_RTOL)

    for w in s.children.values():
        for poly in w.get_polygons():
            if "wall" in poly.name:
                assert np.isclose(abs(poly.vn[0]) , abs(poly.vn[1]))
                assert np.isclose(poly.vn[2] , 0)
