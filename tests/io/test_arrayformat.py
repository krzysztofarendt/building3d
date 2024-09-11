import numpy as np

from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.solid import Solid
from building3d.geom.building import Building
from building3d.io.arrayformat import to_array_format
from building3d.io.arrayformat import from_array_format


def test_arrayformat():
    """Checks if building volume is same before and after reconstruction."""

    # Need to reset the counters before using the array format functions
    Polygon.count = 0
    Wall.count = 0
    Solid.count = 0
    Zone.count = 0
    Building.count = 0

    zone = Zone(
        [
            box(1, 1, 1, (0, 0, 0), "s1"),
            box(1, 2, 1, (1, 0, 0), "s2"),
            box(2, 1, 1, (1, 0, 1), "s3"),
        ],
        "zone",
    )

    building = Building([zone], "building")
    vol1 = building.volume()

    points, faces, polygons, walls, solids, zones = to_array_format(building)
    building = from_array_format(points, faces, polygons, walls, solids, zones)
    vol2 = building.volume()

    assert np.isclose(vol1, vol2)