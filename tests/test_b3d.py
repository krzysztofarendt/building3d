import tempfile

import numpy as np

from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.io.b3d import read_b3d
from building3d.io.b3d import write_b3d


def test_b3d():
    """Saves and reads b3d, checks if the model is the same."""

    with tempfile.TemporaryDirectory() as tmpdirname:
        path = tmpdirname + "/" + "test.b3d"
        # path = "test.b3d"  # for manual investigation only

        solid_1 = box(1, 1, 1, (0, 0, 0), name="Zone_1")
        zone_1 = Zone()
        zone_1.add_solid(solid_1)

        # Add window (subpolygon)
        # TODO: High-level API for adding subpolygons is needed
        wall_path = zone_1.find_wall("wall-0")  # Hardcoded name in box()
        wall = zone_1.get_object(wall_path)
        wall.add_polygon(
            Polygon(
                [
                    Point(0.3, 0.0, 0.0),
                    Point(0.6, 0.0, 0.0),
                    Point(0.6, 0.0, 0.3),
                    Point(0.3, 0.0, 0.6),
                ],
                name="window",
            ),
            parent="wall-0",  # Hardcoded name in box()
        )

        solid_2 = box(1, 1, 1, (1, 0, 0), name="Zone_2")
        zone_2 = Zone()
        zone_2.add_solid(solid_2)
        zones = [zone_1, zone_2]
        building = Building(name="building")
        for z in zones:
            building.add_zone(z)

        building.generate_simulation_mesh(delta=0.3, include_volumes=True)

        write_b3d(path, building)
        b_copy = read_b3d(path)

        # Check geometry
        assert np.isclose(building.volume(), b_copy.volume())
        assert building.name == b_copy.name
        for zname in building.get_zone_names():
            assert zname in b_copy.get_zone_names()
            for sname in building.zones[zname].get_solid_names():
                assert sname in b_copy.zones[zname].get_solid_names()
                vol1 = building.zones[zname].solids[sname].volume
                vol2 = b_copy.zones[zname].solids[sname].volume
                assert np.isclose(vol1, vol2)
                for wall in building.zones[zname].solids[sname].get_walls():
                    b_copy_walls = b_copy.zones[zname].solids[sname].get_walls()
                    assert wall.name in [w.name for w in b_copy_walls]
                    for pname in wall.get_polygon_names():
                        assert pname in wall.get_polygon_names()

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
