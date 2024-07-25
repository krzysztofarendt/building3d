import pytest

from building3d.simulators.rays.ray import Ray
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


def test_ray_moves_closer(single_solid_building):
    position = Point(0.5, 0.5, 0.5)

    # Initialize ray
    ray = Ray(
        position=position,
        building=single_solid_building,
    )
    ray.set_direction(dx=1.0, dy=0.0, dz=0.0)
    ray.update_location()
    ray.update_target_surface()
    ray.update_distance()

    # Move 1 step forward and make sure the ray is closer to the target surface
    d_prev = ray.dist
    ray.forward()
    ray.update_distance()
    d_new = ray.dist
    assert d_new < d_prev

    # Move until it reaches the wall
    while ray.dist > Ray.
