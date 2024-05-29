import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.display.plot_mesh import plot_mesh


def test_building_volume_adjacent():
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (1, 0, 0))  # This zone is adjacent to zone_1
    zones = [zone_1, zone_2]

    expected_volume = 1.0 * len(zones)

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone_instance(z)
    assert np.isclose(bdg.volume(), expected_volume, rtol=GEOM_RTOL)


def test_building_volume_disjoint():
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (2, 2, 2))  # This zone is not adjacent to zone_1
    zones = [zone_1, zone_2]

    expected_volume = 1.0 * len(zones)

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone_instance(z)
    assert np.isclose(bdg.volume(), expected_volume, rtol=GEOM_RTOL)


def test_building_mesh_adjacent(show=False):
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (1, 0, 0))  # This zone is adjacent to zone_1
    zones = [zone_1, zone_2]

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone_instance(z)

    bdg.generate_mesh()
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_mesh(delta=0.3)
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_mesh(delta=0.3, include_volumes=True)
    plot_mesh(bdg.mesh, show=show)


def test_building_mesh_disjoint(show=False):
    zone_1 = box(1, 1, 1, (0, 0, 0))
    zone_2 = box(1, 1, 1, (2, 2, 2))  # This zone is not adjacent to zone_1
    zones = [zone_1, zone_2]

    bdg = Building(name="building")
    for z in zones:
        bdg.add_zone_instance(z)

    bdg.generate_mesh()
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_mesh(delta=0.3)
    plot_mesh(bdg.mesh, show=show)

    bdg.generate_mesh(delta=0.3, include_volumes=True)
    plot_mesh(bdg.mesh, show=show)


if __name__ == "__main__":
    test_building_mesh_adjacent(show=True)
    test_building_mesh_disjoint(show=True)
