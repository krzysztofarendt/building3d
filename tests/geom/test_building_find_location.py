import pytest

from building3d.geom.points import new_point
from building3d.geom.solid.box import box
from building3d.geom.building.find_location import find_location
from building3d.geom.building import Building
from building3d.geom.zone import Zone


@pytest.fixture
def bdg():
    b0 = box(1, 1, 1, (0, 0, 0), name="b0")
    b1 = box(1, 1, 1, (1, 0, 0), name="b1")
    b2 = box(1, 1, 1, (2, 0, 0), name="b2")
    b3 = box(1, 1, 1, (3, 0, 0), name="b3")

    z0 = Zone([b0, b1], name="z0")
    z1 = Zone([b2, b3], name="z1")

    bdg = Building([z0, z1], name="bdg")

    return bdg


def test_point_in_b0(bdg):
    pt = new_point(0.5, 0.5, 0.5)  # z at center
    assert find_location(pt, bdg) == "bdg/z0/b0"
    assert find_location(pt, bdg, "bdg/z0/b0") == "bdg/z0/b0"
    assert find_location(pt, bdg, "bdg/z0/b1") == "bdg/z0/b0"
    assert find_location(pt, bdg, "bdg/z1/b2") == "bdg/z0/b0"
    assert find_location(pt, bdg, "bdg/z1/b3") == "bdg/z0/b0"


def test_point_in_b1(bdg):
    pt = new_point(1.5, 0.5, 0.0)  # z at floor
    assert find_location(pt, bdg) == "bdg/z0/b1"
    assert find_location(pt, bdg, "bdg/z0/b0") == "bdg/z0/b1"
    assert find_location(pt, bdg, "bdg/z0/b1") == "bdg/z0/b1"
    assert find_location(pt, bdg, "bdg/z1/b2") == "bdg/z0/b1"
    assert find_location(pt, bdg, "bdg/z1/b3") == "bdg/z0/b1"


def test_point_in_b2(bdg):
    pt = new_point(2.5, 0.5, 1.0)  # z at ceiling
    assert find_location(pt, bdg) == "bdg/z1/b2"
    assert find_location(pt, bdg, "bdg/z0/b0") == "bdg/z1/b2"
    assert find_location(pt, bdg, "bdg/z0/b1") == "bdg/z1/b2"
    assert find_location(pt, bdg, "bdg/z1/b2") == "bdg/z1/b2"
    assert find_location(pt, bdg, "bdg/z1/b3") == "bdg/z1/b2"


def test_point_in_b3(bdg):
    pt = new_point(3.5, 1.0, 1.0)  # corner
    assert find_location(pt, bdg) == "bdg/z1/b3"
    assert find_location(pt, bdg, "bdg/z1/b3", "bdg/z0/b0") == "bdg/z1/b3"
    assert find_location(pt, bdg, "bdg/z1/b3", "bdg/z0/b0") == "bdg/z1/b3"
    assert find_location(pt, bdg, "bdg/z1/b3", "bdg/z0/b0") == "bdg/z1/b3"
    assert find_location(pt, bdg, "bdg/z1/b3", "bdg/z0/b0") == "bdg/z1/b3"
