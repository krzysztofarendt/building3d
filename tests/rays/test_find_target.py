import numpy as np
import pytest

from building3d.simulators.rays.find_target import find_target
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


def test_find_target_surface_direction(single_solid_building):
    position = Point(0.5, 0.5, 0.5)
    velocity = np.array([1.0, 0.0, 0.0])
    target_1 = find_target(
        position=position,
        velocity=velocity,
        location="zone" + PATH_SEP + "solid",
        building=single_solid_building,
        transparent=[],
        checked_locations=set(),
    )
    assert target_1 is not None and len(target_1) > 0

    position = Point(0.5, 0.5, 0.5)
    velocity = np.array([-1.0, 0.0, 0.0])
    target_2 = find_target(
        position=position,
        velocity=velocity,
        location="zone" + PATH_SEP + "solid",
        building=single_solid_building,
        transparent=[],
        checked_locations=set(),
    )
    assert target_2 is not None and len(target_2) > 0

    assert target_1 != target_2


def test_find_target_edge_direction(single_solid_building):
    position = Point(0.5, 0.5, 0.5)
    velocity = np.array([1.0, 1.0, 0.0])
    target = find_target(
        position=position,
        velocity=velocity,
        location="zone" + PATH_SEP + "solid",
        building=single_solid_building,
        transparent=[],
        checked_locations=set(),
    )
    assert target is not None and len(target) > 0


def test_find_target_corner_direction(single_solid_building):
    position = Point(0.5, 0.5, 0.5)
    velocity = np.array([1.0, 1.0, 1.0])
    target = find_target(
        position=position,
        velocity=velocity,
        location="zone" + PATH_SEP + "solid",
        building=single_solid_building,
        transparent=[],
        checked_locations=set(),
    )
    assert target is not None and len(target) > 0


def test_find_target_incorrect_position(single_solid_building):
    position = Point(1.5, 0.5, 0.5)
    velocity = np.array([1.0, 1.0, 1.0])
    with pytest.raises(RuntimeError):
        _ = find_target(
            position=position,
            velocity=velocity,
            location="zone" + PATH_SEP + "solid",
            building=single_solid_building,
            transparent=[],
            checked_locations=set(),
        )
