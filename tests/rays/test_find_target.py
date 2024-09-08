import numpy as np
import pytest

from building3d.simulators.rays.find_target import find_target
from building3d.simulators.rays.find_transparent import find_transparent
from building3d.geom.points import new_point
from building3d.geom.vectors import new_vector
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid.box import box
from building3d.geom.paths import PATH_SEP


@pytest.fixture
def bdg():
    s0 = box(1, 1, 1, name="s0")
    s1 = box(1, 1, 1, (1, 0, 0), name="s1")
    z = Zone([s0, s1], "z")
    b = Building([z], "b")
    return b


def test_find_target(bdg):
    # Transparent:
    # z/s1/wall-3/wall-3
    # z/s0/wall-1/wall-1
    pos = new_point(0.5, 0.5, 0.5)
    vel = new_vector(1, 0, 0)
    trans = find_transparent(bdg)
    trg = find_target(pos, vel, "b/z/s0", bdg, trans, set())
    assert trg == "b/z/s1/wall-1/wall-1"
    vel = new_vector(-1, 0, 0)
    trg = find_target(pos, vel, "b/z/s0", bdg, trans, set())
    assert trg == "b/z/s0/wall-3/wall-3"

    # Test with large velocity
    mag = 1000.0
    vel = new_vector(mag, 0, 0)
    trg = find_target(pos, vel, "b/z/s0", bdg, trans, set())
    assert trg == "b/z/s1/wall-1/wall-1"
    vel = new_vector(-mag, 0, 0)
    trg = find_target(pos, vel, "b/z/s0", bdg, trans, set())
    assert trg == "b/z/s0/wall-3/wall-3"
