import tempfile

import numpy as np

from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.io.b3d import read_b3d
from building3d.io.b3d import write_b3d


def test_b3d():
    """Saves and reads b3d, checks if the model is the same."""

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = tmpdirname + "/" + "test.b3d"
        # path = "test.b3d"  # for manual investigation only

        zone_1 = box(1, 1, 1, (0, 0, 0), name="Zone_1")
        zone_2 = box(1, 1, 1, (1, 0, 0), name="Zone_2")
        zones = [zone_1, zone_2]
        building = Building(name="building")
        for z in zones:
            building.add_zone_instance(z)

        building.generate_mesh(delta=0.3, include_volumes=True)

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
                for wall in building.zones[zname].solids[sname].walls:
                    b_copy_walls = b_copy.zones[zname].solids[sname].walls
                    assert wall.name in [w.name for w in b_copy_walls]
                    for pname in wall.polygons.keys():
                        assert pname in wall.polygons.keys()

        # Check mesh
        assert len(building.mesh.polymesh.vertices) == len(
            b_copy.mesh.polymesh.vertices
        )
        assert len(building.mesh.polymesh.faces) == len(b_copy.mesh.polymesh.faces)
        assert len(building.mesh.solidmesh.vertices) == len(
            b_copy.mesh.solidmesh.vertices
        )
        assert len(building.mesh.solidmesh.elements) == len(
            b_copy.mesh.solidmesh.elements
        )


if __name__ == "__main__":
    test_b3d()
