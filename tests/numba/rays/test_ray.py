import numpy as np
import pytest

from building3d.simulators.rays.numba.ray import Ray
from building3d.geom.numba.points import new_point
from building3d.geom.numba.building import Building
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.solid.box import box
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
