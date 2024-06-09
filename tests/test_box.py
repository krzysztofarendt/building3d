import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.predefined.box import box


def test_one_box():
    b = box(1, 1, 1, (0, 0, 0))
    assert np.isclose(b.volume(), 1, rtol=GEOM_RTOL)
    assert len(b.solids.keys()) == 1
    assert b.name is not None
    assert len(b.name) > 0


def test_two_boxes():
    b1 = box(1, 1, 1, (0, 0, 0))
    b2 = box(1, 1, 1, (1, 0, 0))
    assert np.isclose(b1.volume(), 1, rtol=GEOM_RTOL)
    assert np.isclose(b2.volume(), 1, rtol=GEOM_RTOL)

    assert len(b1.solids.keys()) == 1
    assert len(b2.solids.keys()) == 1

    assert b1.name != b2.name
    assert list(b1.solids.values())[0].name != list(b2.solids.values())[0].name
