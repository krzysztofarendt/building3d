import tempfile

import numpy as np

from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.io.stl import read_stl
from building3d.io.stl import write_stl


def test_stl():
    """Saves and reads STL, checks if the zone is the same."""

    with tempfile.TemporaryDirectory() as tmpdirname:
        solid = box(1.0, 1.0, 1.0)
        zone = Zone()
        zone.add_solid(solid)
        stl_path = tmpdirname + "/" + zone.name + ".stl"
        write_stl(stl_path, zone)

        zone_recovered = read_stl(stl_path)

        # Check if both zones have the same volume
        # (polygons cannot be compared, because STL format changes polygon structure)
        vol1 = zone.volume()
        vol2 = zone_recovered.volume()
        assert np.isclose(vol1, vol2), f"Volumes different: {vol1} != {vol2}"
