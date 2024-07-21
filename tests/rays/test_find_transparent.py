from building3d.simulators.rays.find_transparent import find_transparent
from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone


def test_find_transparent_1_solid():
    xlim = 5
    ylim = 5
    zlim = 3
    solid_1 = box(xlim, ylim, zlim, name="solid_1")

    zone = Zone("zone")
    zone.add_solid(solid_1)

    building = Building(name="building")
    building.add_zone(zone)

    transp = find_transparent(building)
    assert len(transp) == 0


def test_find_transparent_2_solids():
    xlim = 5
    ylim = 5
    zlim = 3
    solid_1 = box(xlim, ylim, zlim, name="solid_1")
    xlim = 5
    ylim = 5
    zlim = 3
    solid_2 = box(xlim, ylim, zlim, (5, 0, 0), name="solid_2")

    zone = Zone("zone")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)

    building = Building(name="building")
    building.add_zone(zone)

    transp = find_transparent(building)
    assert len(transp) == 2


def test_find_transparent_3_solids():
    xlim = 5
    ylim = 5
    zlim = 3
    solid_1 = box(xlim, ylim, zlim, name="solid_1")
    xlim = 5
    ylim = 5
    zlim = 3
    solid_2 = box(xlim, ylim, zlim, (5, 0, 0), name="solid_2")
    xlim = 5
    ylim = 5
    zlim = 3
    solid_3 = box(xlim, ylim, zlim, (5, 5, 0), name="solid_3")

    zone = Zone("zone")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)
    zone.add_solid(solid_3)

    building = Building(name="building")
    building.add_zone(zone)

    transp = find_transparent(building)
    assert len(transp) == 4


if __name__ == "__main__":
    test_find_transparent_2_solids()
