import tempfile

import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.io.dotbim import read_dotbim
from building3d.io.dotbim import write_dotbim


def test_dotbim():
    """Saves and reads dotbim, checks if the model is the same."""

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = tmpdirname + "/" + "building.bim"

        zone_1 = box(1, 1, 1, (0, 0, 0), name="Zone_1")
        zone_2 = box(1, 1, 1, (1, 0, 0), name="Zone_2")
        zones = [zone_1, zone_2]
        building = Building(name="building")
        for z in zones:
            building.add_zone(z)

        write_dotbim(path, building)

        building_copy = read_dotbim(path)

        assert np.isclose(building.volume(), building_copy.volume(), rtol=GEOM_RTOL)
        assert building.name == building_copy.name
        for zone_name in building.zones.keys():
            assert zone_name in building_copy.zones.keys()
            # TODO: Add deep check (solids, walls, polygons)
            ...
