import pytest

from building3d.simulators.rays.manyrays import ManyRays
from building3d.geom.point import Point
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.predefined.solids.box import box
from building3d.geom.paths import PATH_SEP


@pytest.fixture
def single_solid_building():
    solid = box(1, 1, 1, name="solid")
    zone = Zone("zone")
    zone.add_solid(solid)
    bdg = Building()
    bdg.add_zone(zone)
    return bdg


@pytest.fixture
def double_solid_building():
    solid1 = box(1, 1, 1, name="solid-1")
    solid2 = box(1, 1, 1, (1.0, 0.0, 0.0), name="solid-2")
    zone = Zone("zone")
    zone.add_solid(solid1)
    zone.add_solid(solid2)
    bdg = Building()
    bdg.add_zone(zone)
    return bdg


def test_manyrays_init_location_single_solid(single_solid_building):
    num_rays = 10
    source = Point(0.5, 0.5, 0.5)
    rays = ManyRays(num_rays, source, single_solid_building)
    rays.set_omnidirectional_source()
    assert len(rays) == num_rays
    for i in range(num_rays):
        assert rays[i].location == "zone/solid"


def test_manyrays_init_location_double_solid(double_solid_building):
    num_rays = 10
    source = Point(0.5, 0.5, 0.5)
    rays = ManyRays(num_rays, source, double_solid_building)
    rays.set_omnidirectional_source()
    assert len(rays) == num_rays
    for i in range(num_rays):
        assert rays[i].location == "zone/solid-1"

    num_rays = 10
    source = Point(1.5, 0.5, 0.5)
    rays = ManyRays(num_rays, source, double_solid_building)
    rays.set_omnidirectional_source()
    assert len(rays) == num_rays
    for i in range(num_rays):
        assert rays[i].location == "zone/solid-2"
