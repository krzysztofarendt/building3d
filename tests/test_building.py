import numpy as np
import pytest

from building3d.config import GEOM_RTOL
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.predefined.solids.box import box
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone


def test_building_volume_adjacent():
    solid_1 = box(1, 1, 1, (0, 0, 0))
    solid_2 = box(1, 1, 1, (1, 0, 0))  # This zone is adjacent to zone_1
    zone_1 = Zone()
    zone_2 = Zone()
    zone_1.add_solid(solid_1)
    zone_2.add_solid(solid_2)
    zones = [zone_1, zone_2]

    expected_volume = 1.0 * len(zones)

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone(z)
    assert np.isclose(bdg.volume(), expected_volume, rtol=GEOM_RTOL)


def test_building_volume_disjoint():
    solid_1 = box(1, 1, 1, (0, 0, 0))
    solid_2 = box(1, 1, 1, (2, 2, 2))  # This zone is not adjacent to zone_1
    zone_1 = Zone()
    zone_2 = Zone()
    zone_1.add_solid(solid_1)
    zone_2.add_solid(solid_2)
    zones = [zone_1, zone_2]

    expected_volume = 1.0 * len(zones)

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone(z)
    assert np.isclose(bdg.volume(), expected_volume, rtol=GEOM_RTOL)


def test_building_mesh_adjacent(show=False):
    solid_1 = box(1, 1, 1, (0, 0, 0))
    solid_2 = box(1, 1, 1, (1, 0, 0))  # This zone is adjacent to zone_1
    zone_1 = Zone()
    zone_2 = Zone()
    zone_1.add_solid(solid_1)
    zone_2.add_solid(solid_2)
    zones = [zone_1, zone_2]

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone(z)

    bdg.generate_simulation_mesh()
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_simulation_mesh(delta=0.3)
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_simulation_mesh(delta=0.3, include_volumes=True)
    plot_mesh(bdg.mesh, show=show)


def test_building_mesh_disjoint(show=False):
    solid_1 = box(1, 1, 1, (0, 0, 0))
    solid_2 = box(1, 1, 1, (2, 2, 2))  # This zone is not adjacent to zone_1
    zone_1 = Zone()
    zone_2 = Zone()
    zone_1.add_solid(solid_1)
    zone_2.add_solid(solid_2)
    zones = [zone_1, zone_2]

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone(z)

    bdg.generate_simulation_mesh()
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_simulation_mesh(delta=0.3)
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_simulation_mesh(delta=0.3, include_volumes=True)
    plot_mesh(bdg.mesh, show=show)


def test_get_object():
    """The tested function is recursive, so this test covers
    the `get_object` method in all: Building, Zone, Solid, Wall."""

    sld = box(1, 1, 1, (0, 0, 0), name="test_name")
    zone = Zone(name="test_name")
    zone.add_solid(sld)
    bdg = Building(name="building")
    bdg.add_zone(zone)

    obj = bdg.get_object("test_name/test_name/floor/floor")
    assert type(obj) is Polygon

    obj = bdg.get_object("test_name/test_name/floor")
    assert type(obj) is Wall

    obj = bdg.get_object("test_name/test_name")
    assert type(obj) is Solid

    obj = bdg.get_object("test_name")
    assert type(obj) is Zone

    with pytest.raises(ValueError):
        obj = bdg.get_object("xxx")

    with pytest.raises(ValueError):
        obj = bdg.get_object("test_name/test_name/floor/xxx")

    with pytest.raises(ValueError):
        obj = bdg.get_object("test_name/test_name/floor/floor/xxx")


def test_equality():
    s1 = box(1, 1, 1)
    z1 = Zone()
    z1.add_solid(s1)
    b1 = Building()
    b1.add_zone(z1)

    s2 = box(1, 1, 1)
    z2 = Zone()
    z2.add_solid(s2)
    b2 = Building()
    b2.add_zone(z2)
    assert b1 == b2

    s3 = box(1, 1, 1, (1, 1, 1))
    z3 = Zone()
    z3.add_solid(s3)
    b3 = Building()
    b3.add_zone(z3)
    assert b1 != b3

    b4 = Building()
    b4.add_zone(z1)

    assert b4 == b1


def test_building_find_adjacent_solids():
    # Geometry from examples/example_5.py
    solid_1 = box(5, 5, 3, name="s1")
    solid_2 = box(3, 3, 2, (5, 1, 0), name="s2")
    solid_3 = box(3, 3, 2, (0, 5, 0), name="s3")
    solid_4 = box(3, 3, 2, (1, 1, 3), name="s4")
    solid_5 = box(1, 1, 1, (0.5, 0.5, 5), name="s5")
    solid_6 = box(1, 1, 1, (5, 0, 0), name="s6")
    zone = Zone("z")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)
    zone.add_solid(solid_3)
    zone.add_solid(solid_4)
    zone.add_solid(solid_5)
    zone.add_solid(solid_6)
    building = Building(name="building")
    building.add_zone(zone)
    adj = building.find_adjacent_solids()
    assert "z/s2" in adj["z/s1"]
    assert "z/s1" in adj["z/s2"]

    assert "z/s3" in adj["z/s1"]
    assert "z/s1" in adj["z/s3"]

    assert "z/s4" in adj["z/s1"]
    assert "z/s1" in adj["z/s4"]

    assert "z/s5" in adj["z/s4"]
    assert "z/s4" in adj["z/s5"]

    assert "z/s6" in adj["z/s1"]
    assert "z/s1" in adj["z/s6"]

    assert "z/s6" in adj["z/s2"]
    assert "z/s2" in adj["z/s6"]


def test_building_stitch_solids():
    # Geometry from examples/example_5.py
    solid_1 = box(5, 5, 3, name="s1")
    original_number_of_polys = len(solid_1.get_polygons())

    solid_2 = box(3, 3, 2, (5, 1, 0), name="s2")
    solid_3 = box(3, 3, 2, (0, 5, 0), name="s3")
    solid_4 = box(3, 3, 2, (1, 1, 3), name="s4")
    solid_5 = box(1, 1, 1, (0.5, 0.5, 5), name="s5")
    solid_6 = box(1, 1, 1, (5, 0, 0), name="s6")
    zone = Zone("z")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)
    zone.add_solid(solid_3)
    zone.add_solid(solid_4)
    zone.add_solid(solid_5)
    zone.add_solid(solid_6)
    building = Building(name="building")
    building.add_zone(zone)
    building.stitch_solids()  # Just testing if there are no errors

    # Testing if solid s1 has more polygons after stitching
    s1 = building.get_object("z/s1")
    assert isinstance(s1, Solid)
    new_number_of_polys = len(s1.get_polygons())
    assert new_number_of_polys > original_number_of_polys


if __name__ == "__main__":
    test_building_mesh_adjacent(show=True)
    test_building_mesh_disjoint(show=True)
