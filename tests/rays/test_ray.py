import pytest

from building3d.simulators.rays.ray import Ray
from building3d.geom.point import Point
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.predefined.solids.box import box


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


def test_ray(single_solid_building):
    position = Point(0.5, 0.5, 0.5)
    ray = Ray(
        position=position,
        building=single_solid_building,
    )
    ray.set_direction(dx=1.0, dy=0.0, dz=0.0)
    # ray.forward()  # TODO: Doesn't work
