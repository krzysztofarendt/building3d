import tempfile

import numpy as np

from building3d.geom.building import Building
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.io.b3d import read_b3d
from building3d.io.b3d import write_b3d


def test_b3d():
    """Saves and reads b3d, checks if the model is the same."""

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = tmpdirname + "/" + "test.b3d"
        # path = "test.b3d"  # for manual investigation only

        solid_1 = box(1, 1, 1, (0, 0, 0), name="solid-1")
        zone_1 = Zone(name="zone-1")
        zone_1.add_solid(solid_1)

        solid_2 = box(1, 1, 1, (1, 0, 0), name="solid-2")
        zone_2 = Zone(name="zone-2")
        zone_2.add_solid(solid_2)
        zones = [zone_1, zone_2]
        building = Building(name="building")
        for z in zones:
            building.add_zone(z)

        write_b3d(path, building)
        b_copy = read_b3d(path)

        # Check geometry
        assert np.isclose(building.volume(), b_copy.volume())
        assert building.name == b_copy.name
        for zname in building.zones.keys():
            assert zname in b_copy.zones.keys()
            for sname in building.zones[zname].solids.keys():
                assert sname in b_copy.zones[zname].solids.keys()
                vol1 = building.zones[zname].solids[sname].volume
                vol2 = b_copy.zones[zname].solids[sname].volume
                assert np.isclose(vol1, vol2)
                for wall in building.zones[zname].solids[sname].walls.values():
                    b_copy_walls = b_copy.zones[zname].solids[sname].walls.values()
                    assert wall.name in [w.name for w in b_copy_walls]
                    for pname in wall.polygons.keys():
                        assert pname in wall.polygons.keys()


if __name__ == "__main__":
    test_b3d()
