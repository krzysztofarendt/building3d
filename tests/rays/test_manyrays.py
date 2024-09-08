import pytest

import numpy as np

from building3d.simulators.rays.manyrays import ManyRays
from building3d.geom.points import new_point
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid.box import box


@pytest.fixture
def manyrays_single_solid_building():
    solid = box(1, 1, 1, name="s")
    zone = Zone([solid], "z")
    bdg = Building([zone], name="b")
    return bdg


@pytest.fixture
def manyrays_double_solid_building():
    s0 = box(1, 1, 1, name="s0")
    s1 = box(1, 1, 1, (1.0, 0.0, 0.0), name="s1")
    z = Zone([s0, s1], "z")
    bdg = Building([z], "b")
    return bdg


def test_manyrays_init_position_single_solid(manyrays_single_solid_building):
    bdg = manyrays_single_solid_building
    num_rays = 10
    source = new_point(0.5, 0.5, 0.5)
    rays = ManyRays(num_rays, source, bdg)
    assert len(rays) == num_rays
    for i in range(num_rays):
        assert np.allclose(rays[i].pos, source)


def test_manyrays_init_position_double_solid(manyrays_double_solid_building):
    bdg = manyrays_double_solid_building
    num_rays = 10
    source = new_point(0.5, 0.5, 0.5)
    rays = ManyRays(num_rays, source, bdg)
    assert len(rays) == num_rays
    for i in range(num_rays):
        assert np.allclose(rays[i].pos, source)

    num_rays = 10
    source = new_point(1.5, 0.5, 0.5)
    rays = ManyRays(num_rays, source, bdg)
    assert len(rays) == num_rays
    for i in range(num_rays):
        assert np.allclose(rays[i].pos, source)

