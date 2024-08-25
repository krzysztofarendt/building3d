import numpy as np
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


def move_and_reflect(ray, max_room_dim):
    # Move 1 step forward and make sure the ray is closer to the target surface
    d_prev = ray.dist
    ray.forward()
    d_new = ray.dist
    assert d_new < d_prev

    # Move until it reaches the wall, make sure it is reflected
    prev_velocity = ray.velocity.copy()
    prev_position = ray.position.copy()
    max_num_steps = max_room_dim / (Ray.speed * Ray.time_step)

    step = 0
    while True:
        print(f"{step=}, {ray}")
        ray.forward()
        assert prev_position != ray.position, f"Ray not moving? ({step=})"

        if not np.isclose(ray.velocity, prev_velocity).all():
            assert (
                ray.num_steps_after_contact == 1
            ), f"Something's wrong with the reflection logic: {ray.num_steps_after_contact=}"
            break

        prev_position = ray.position.copy()
        prev_velocity = ray.velocity.copy()

        step += 1
        if step > max_num_steps:
            raise RuntimeError(
                f"Ray is moving for too long ({step} steps) without a reflection."
            )


def test_ray_single_solid_building(single_solid_building):
    position = Point(0.5, 0.5, 0.5)

    test_directions = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.9, 0.5, 0.3),
        (1.0, 1.0, 1.0),
        (1.0, 0.0, 1.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 1.0),
        (-1.0, -1.0, -1.0),
    ]

    for d in test_directions:
        ray = Ray(position=position, building=single_solid_building)
        ray.set_direction(dx=d[0], dy=d[1], dz=d[2])
        ray.update_location()
        move_and_reflect(ray, max_room_dim=1)


def test_ray_double_solid_building(double_solid_building):
    position = Point(0.5, 0.5, 0.5)

    test_directions = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.9, 0.5, 0.3),
        (1.0, 1.0, 1.0),
        (1.0, 0.0, 1.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 1.0),
        (-1.0, -1.0, -1.0),
    ]

    for d in test_directions:
        ray = Ray(position=position, building=double_solid_building)
        ray.set_direction(dx=d[0], dy=d[1], dz=d[2])
        ray.update_location()
        move_and_reflect(ray, max_room_dim=2)
