import numpy as np
import pytest

from building3d.config import GEOM_RTOL
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.predefined.box import box


def test_building_volume_adjacent():
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (1, 0, 0))  # This zone is adjacent to zone_1
    zones = [zone_1, zone_2]

    expected_volume = 1.0 * len(zones)

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone(z)
    assert np.isclose(bdg.volume(), expected_volume, rtol=GEOM_RTOL)


def test_building_volume_disjoint():
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (2, 2, 2))  # This zone is not adjacent to zone_1
    zones = [zone_1, zone_2]

    expected_volume = 1.0 * len(zones)

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone(z)
    assert np.isclose(bdg.volume(), expected_volume, rtol=GEOM_RTOL)


def test_building_mesh_adjacent(show=False):
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (1, 0, 0))  # This zone is adjacent to zone_1
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
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (2, 2, 2))  # This zone is not adjacent to zone_1
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

    zone = box(1, 1, 1, (0, 0, 0), name="test_name")
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

    obj = bdg.get_object("xxx")
    assert obj is None

    obj = bdg.get_object("test_name/test_name/floor/xxx")
    assert obj is None

    with pytest.raises(ValueError):
        obj = bdg.get_object("test_name/test_name/floor/floor/xxx")


if __name__ == "__main__":
    test_building_mesh_adjacent(show=True)
    test_building_mesh_disjoint(show=True)
