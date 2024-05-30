import tempfile

import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.io.b3d import read_b3d
from building3d.io.b3d import write_b3d


def test_b3d():
    """Saves and reads b3d, checks if the model is the same."""

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = tmpdirname + "/" + "test.b3d"
        path = "test.b3d"  # TODO: Delete

        zone_1 = box(1, 1, 1, (0, 0, 0), name="Zone_1")
        zone_2 = box(1, 1, 1, (1, 0, 0), name="Zone_2")
        zones = [zone_1, zone_2]
        building = Building(name="building")
        for z in zones:
            building.add_zone_instance(z)

        building.generate_mesh(delta=0.3, include_volumes=True)

        write_b3d(path, building)

        # raise  # TODO: The rest of the function is not ready yet
        # building_copy = read(path)
        # assert np.isclose(building.volume(), building_copy.volume(), rtol=GEOM_RTOL)
        # assert building.name == building_copy.name
        # for zone_name in building.zones.keys():
        #     assert zone_name in building_copy.zones.keys()
        #     # TODO: Add deep check (solids, walls, polygons)
        #     ...


if __name__ == "__main__":
    test_b3d()
