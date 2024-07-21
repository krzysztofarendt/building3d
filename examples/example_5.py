from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.operations.stitch_solids import stitch_solids
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone

if __name__ == "__main__":
    solid_1 = box(5, 5, 3, name="solid_1")
    solid_2 = box(3, 3, 2, (5, 1, 0), name="solid_2")
    solid_3 = box(3, 3, 2, (0, 5, 0), name="solid_3")
    solid_4 = box(3, 3, 2, (1, 1, 3), name="solid_4")
    solid_5 = box(1, 1, 1, (0.5, 0.5, 5), name="solid_5")
    solid_6 = box(1, 1, 1, (5, 0, 0), name="solid_6")

    # Below operations are now done automatically in building.stitch_solids()
    # solid_1, solid_2 = stitch_solids(solid_1, solid_2)
    # solid_1, solid_3 = stitch_solids(solid_1, solid_3)
    # solid_1, solid_4 = stitch_solids(solid_1, solid_4)
    # solid_4, solid_5 = stitch_solids(solid_4, solid_5)
    # solid_1, solid_6 = stitch_solids(solid_1, solid_6)
    # solid_2, solid_6 = stitch_solids(solid_2, solid_6)

    zone = Zone("zone")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)
    zone.add_solid(solid_3)
    zone.add_solid(solid_4)
    zone.add_solid(solid_5)
    zone.add_solid(solid_6)

    building = Building(name="building")
    building.add_zone(zone)

    # Plot model before stitching solids
    plot_objects((building, ))

    # Stitch and plot again
    building.stitch_solids()
    plot_objects((building, ))

    # Plot again, but use random color for each solid
    plot_objects(tuple(zone.get_solids()))
