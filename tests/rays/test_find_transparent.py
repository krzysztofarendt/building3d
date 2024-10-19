from building3d.sim.rays.find_transparent import find_transparent
from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone


def test_find_transparent():
    """Tests if all transparent polygons in a building are found.

    Transparent polygons are those, which are facing each other within a single zone.
    """
    s0 = box(1.0, 1.0, 1.0, (0.0, 0.0, 0.0), name="s0")
    s1 = box(1.0, 1.0, 1.0, (1.0, 0.0, 0.0), name="s1")
    zone = Zone([s0, s1], name="z")
    building = Building([zone], name="b")

    # There should be only two adjacent polygons within a zone
    transparent = find_transparent(building)
    assert len(transparent) == 2

    # These polygons should be facing
    poly0 = building.get(transparent.pop())
    poly1 = building.get(transparent.pop())
    assert isinstance(poly0, Polygon)
    assert isinstance(poly1, Polygon)
    assert poly0.is_facing_polygon(poly1)
    assert poly1.is_facing_polygon(poly0)
