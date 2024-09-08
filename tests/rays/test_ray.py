import numpy as np
import pytest

from building3d import random_between
from building3d.simulators.rays.ray import Ray
from building3d.geom.points import new_point
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid.box import box
from building3d.geom.paths import PATH_SEP



@pytest.fixture
def single_solid_building():
    s = box(1, 1, 1, name="s")
    z = Zone([s], "z")
    b = Building([z], "b")
    return b


@pytest.fixture
def double_solid_building():
    s0 = box(1, 1, 1, name="s0")
    s1 = box(1, 1, 1, (1.0, 0.0, 0.0), name="s1")
    z = Zone([s0, s1], "z")
    b = Building([z], "b")
    return b


def test_ray_init(double_solid_building):
    bdg = double_solid_building
    pos = new_point(0.5, 0.5, 0.5)
    ray = Ray(pos, bdg)

    # Make sure transparent surfaces are found
    assert "b/z/s0/wall-1/wall-1" in ray.transparent
    assert "b/z/s1/wall-3/wall-3" in ray.transparent

    # Make sure location is empty
    # (it shouldn't be auto-calculated, because it is slow; it's better to assign it explicitly)
    assert ray.loc == ""

    # Find current solid and check location again
    ray.update_location()
    assert ray.loc == "b/z/s0"

    # Make sure target surface is not known yet (ray is not moving)
    assert ray.trg_surf == ""

    # Assign velocity and find target surface
    ray.vel[0] = 1.0  # x
    ray.update_target_surface()
    assert ray.trg_surf == "b/z/s1/wall-1/wall-1"

    # Calculate distance to target surface
    ray.update_distance(fast_calc=False)
    assert np.isclose(ray.dist, 1.5)

    # Change direction and again find target surface and distance
    ray.vel[0] = -1.0  # x
    ray.update_target_surface()
    assert ray.trg_surf == "b/z/s0/wall-3/wall-3"

    ray.update_distance(fast_calc=False)
    assert np.isclose(ray.dist, 0.5)


def test_ray_set_direction(single_solid_building):
    bdg = single_solid_building
    pos = new_point(0.5, 0.5, 0.5)
    ray = Ray(pos, bdg)
    ray.set_direction(1, 0, 0)
    assert np.allclose(ray.vel, [Ray.speed * Ray.time_step, 0, 0])


def test_ray_forward_and_reflect(single_solid_building):
    # Initialize building and ray
    bdg = single_solid_building
    pos = new_point(0.5, 0.5, 0.5)
    ray = Ray(pos, bdg)
    ray.set_direction(1, 0, 0)
    ray.update_location()
    ray.update_target_surface()
    ray.update_distance(fast_calc=False)

    # Move forward for as many steps as possible without reflection
    dist_without_reflect = ray.dist - Ray.min_dist
    num_steps_to_surf = int(np.floor(dist_without_reflect / ray.speed / ray.time_step))

    for _ in range(num_steps_to_surf):
        ray.forward()
        assert np.allclose(ray.vel, (Ray.speed * Ray.time_step, 0, 0))

    # Reflection should not happen after the next step, because the ray first checks
    # if it is close the surface, and if not, it moves forward
    ray.forward()
    assert np.allclose(ray.vel, (Ray.speed * Ray.time_step, 0, 0))

    # But now the ray will reflect
    ray.forward()
    assert np.allclose(ray.vel, (-Ray.speed * Ray.time_step, 0, 0))


def test_ray_forward_and_reflect_going_towards_corner(single_solid_building):
    # Initialize building and ray
    bdg = single_solid_building
    pos = new_point(0.5, 0.5, 0.5)
    ray = Ray(pos, bdg)
    ray.set_direction(1, 1, 0)
    ray.update_location()
    ray.update_target_surface()
    ray.update_distance(fast_calc=False)

    # Move forward for as many steps as possible without reflection
    expected = Ray.speed * Ray.time_step / np.sqrt(2.)
    while np.allclose(ray.vel, (expected, expected, 0)):
        ray.forward()

    # Ray reflected, make sure the direction is reversed
    assert np.allclose(ray.vel, (-expected, -expected, 0))


def test_ray_forward_and_reflect_going_random_direction(single_solid_building):
    # Initialize building and ray
    bdg = single_solid_building
    pos = new_point(0.5, 0.5, 0.5)
    ray = Ray(pos, bdg)

    for _ in range(10):
        p = np.clip(np.random.random(3), 0.1, 0.9)
        pos = new_point(*p)
        ray = Ray(pos, bdg)
        ray.set_direction(
            dx=random_between(-1, 1),
            dy=random_between(-1, 1),
            dz=random_between(-1, 1),
        )
        ray.update_location()
        ray.update_target_surface()
        ray.update_distance(fast_calc=False)
        init_vel = ray.vel.copy()

        # Move forward for as many steps as possible without reflection
        while np.allclose(ray.vel, init_vel):
            ray.forward()

        # Reflect and move a bit
        for _ in range(20):
            ray.forward()
