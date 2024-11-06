from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from building3d.io.stl import read_stl, write_stl
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.building import Building


def test_stl_single_solid():
    solid = box(1, 1, 1)
    zone = Zone([solid])
    building = Building([zone])

    output_file = None
    with TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "building.stl"
        write_stl(str(output_file), building)
        assert output_file.exists()

        # Test reading
        new_building = read_stl(str(output_file))
        assert isinstance(new_building, Building)

        # STL format doesn't contain information about triangle ownership,
        # so each triangle is a separate polygon and wall.
        # A cube has 6 sides, each with 2 triangles, so the number of polygons will be 12.
        assert len(new_building.get_polygon_paths()) == 12

        # However, both buildings should have same volume
        assert np.isclose(new_building.volume(), building.volume())


def test_stl_two_solids():
    solid_1 = box(1, 1, 1)
    solid_2 = box(1, 1, 1, (1, 0, 0))
    zone = Zone([solid_1, solid_2])
    building = Building([zone])

    output_file = None
    with TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "building.stl"
        write_stl(str(output_file), building)
        assert output_file.exists()

        # Test reading
        new_building = read_stl(str(output_file))
        assert isinstance(new_building, Building)

        # STL format doesn't contain information about triangle ownership,
        # so each triangle is a separate polygon and wall.
        # There are 2 cubes, each cube has 6 sides, each with 2 triangles,
        # so the number of polygons will be 24.
        assert len(new_building.get_polygon_paths()) == 24

        # However, both buildings should have same volume
        assert np.isclose(new_building.volume(), building.volume())
