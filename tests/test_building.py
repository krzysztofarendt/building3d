import numpy as np

from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.config import GEOM_RTOL


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
