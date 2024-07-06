from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.operations.stitch_solids import stitch_solids
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.geom.point import Point
from building3d.rays.ray import Ray
from building3d.rays.ray import RayCluster

if __name__ == "__main__":
    solid_1 = box(5, 5, 3, name="solid_1")

    zone = Zone("zone")
    zone.add_solid(solid_1)

    building = Building(name="building")
    building.add_zone(zone)

    r = Ray(Point(2, 2, 2))
    rc = RayCluster([r])

    # Plot model before stitching solids
    plot_objects(building, rc)
