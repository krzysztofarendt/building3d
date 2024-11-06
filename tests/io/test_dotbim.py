from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from building3d.io.dotbim import read_dotbim, write_dotbim
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.building import Building


def test_stl_single_solid():
    solid = box(1, 1, 1)
    zone = Zone([solid])
    building = Building([zone])

    output_file = None
    with TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "building.bim"
        write_dotbim(str(output_file), building)
        assert output_file.exists()

        # Test reading
        new_building = read_dotbim(str(output_file))
        assert isinstance(new_building, Building)

        # .bim format contains information about triangle ownership in the metadata.
        # This metadata is present only when the .bim file is exported by building3d.
        # .bim files from other programs will be treated as STL - with each triangle
        # as a separate polygon and wall. (TODO)
        assert len(building.get_polygon_paths()) == len(new_building.get_polygon_paths())

        # However, both buildings should have same volume
        assert np.isclose(new_building.volume(), building.volume())


def test_stl_two_solids():
    solid_1 = box(1, 1, 1)
    solid_2 = box(1, 1, 1, (1, 0, 0))
    zone = Zone([solid_1, solid_2])
    building = Building([zone])

    output_file = None
    with TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "building.bim"
        write_dotbim(str(output_file), building)
        assert output_file.exists()

        # Test reading
        new_building = read_dotbim(str(output_file))
        assert isinstance(new_building, Building)

        # .bim format contains information about triangle ownership in the metadata.
        # This metadata is present only when the .bim file is exported by building3d.
        # .bim files from other programs will be treated as STL - with each triangle
        # as a separate polygon and wall. (TODO)
        assert len(building.get_polygon_paths()) == len(new_building.get_polygon_paths())

        # However, both buildings should have same volume
        assert np.isclose(new_building.volume(), building.volume())
