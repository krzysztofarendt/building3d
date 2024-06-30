import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.predefined.solids.box import box


def test_one_box():
    b = box(1, 1, 1, (0, 0, 0))
    assert np.isclose(b.volume, 1, rtol=GEOM_RTOL)
    assert len(b.walls.keys()) == 6
    assert b.name is not None
    assert len(b.name) > 0


def test_two_boxes():
    b1 = box(1, 1, 1, (0, 0, 0))
    b2 = box(1, 1, 1, (1, 0, 0))
    assert np.isclose(b1.volume, 1, rtol=GEOM_RTOL)
    assert np.isclose(b2.volume, 1, rtol=GEOM_RTOL)

    assert len(b1.walls.keys()) == 6
    assert len(b2.walls.keys()) == 6

    assert b1.name != b2.name
    assert list(b1.walls.values())[0].name == list(b2.walls.values())[0].name
    assert list(b1.walls.values())[0].uid != list(b2.walls.values())[0].uid
