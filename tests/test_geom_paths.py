import pytest

from building3d.geom.paths.validate_name import validate_name
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths import PATH_SEP
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.point import Point


def test_validate_name():
    assert isinstance(validate_name("testname"), str)
    assert isinstance(validate_name("test-name"), str)
    assert isinstance(validate_name("test_name"), str)
    r = validate_name("test-name")
    assert r == "test-name"
    with pytest.raises(ValueError):
        _ = validate_name("test/name")
    with pytest.raises(ValueError):
        _ = validate_name("/testname")
    with pytest.raises(ValueError):
        _ = validate_name("testname/")


def test_object_path():
    p0 = Point(0, 0, 0)
    p1 = Point(1, 0, 0)
    p2 = Point(1, 1, 0)
    poly = Polygon([p0, p1, p2], name="polygon")
    wall = Wall([poly], name="wall")
    solid = Solid([wall], name="solid", verify=False)  # It is not a valid solid, so don't verify
    zone = Zone(name="zone", verify=False)  # It is not a valid zone, so don't verify
    zone.add_solid(solid)
    building = Building(name="building")
    building.add_zone(zone)

    path = object_path(
        zone=zone,
        solid=solid,
        wall=wall,
        poly=poly,
    )
    assert path == "zone" + PATH_SEP + "solid" + PATH_SEP + "wall" + PATH_SEP + "polygon"

    path = object_path(
        solid=solid,
        wall=wall,
        poly=poly,
    )
    assert path == "solid" + PATH_SEP + "wall" + PATH_SEP + "polygon"

    path = object_path(
        wall=wall,
        poly=poly,
    )
    assert path == "wall" + PATH_SEP + "polygon"

    path = object_path(
        poly=poly,
    )
    assert path == "polygon"

    path = object_path(
        zone=zone,
        solid=solid,
        wall=wall,
    )
    assert path == "zone" + PATH_SEP + "solid" + PATH_SEP + "wall"

    path = object_path(
        zone=zone,
        solid=solid,
    )
    assert path == "zone" + PATH_SEP + "solid"

    path = object_path(
        zone=zone,
    )
    assert path == "zone"

    path = object_path(
        wall=wall,
    )
    assert path == "wall"
