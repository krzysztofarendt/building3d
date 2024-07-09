from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.geom.point import Point
from building3d.simulators.rays.simulator import RaySimulator


if __name__ == "__main__":
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

    raysim = RaySimulator(
        building = building,
        source = Point(1, 1, 1),
        receiver = Point(3, 3, 2),
        receiver_radius = 1,
        num_rays = 10000,
        speed = 343.0,
        time_step = 1e-4,
    )
    for i in range(50):
        raysim.forward()

    plot_objects(building, raysim.r_cluster)
