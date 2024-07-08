from building3d import random_between
from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.geom.point import Point
from building3d.simulators.rays.ray import Ray
from building3d.simulators.rays.cluster import RayCluster


if __name__ == "__main__":
    xlim = 5
    ylim = 5
    zlim = 3
    solid_1 = box(xlim, ylim, zlim, name="solid_1")

    zone = Zone("zone")
    zone.add_solid(solid_1)

    building = Building(name="building")
    building.add_zone(zone)

    rays = []
    num_rays = 10000
    time_step = 1

    for _ in range(num_rays):
        rx = random_between(0, xlim)
        ry = random_between(0, ylim)
        rz = random_between(0, zlim)
        ray = Ray(Point(rx, ry, rz), time_step)

        ray.set_speed(random_between(0, 1))

        dx = random_between(-1, 1)
        dy = random_between(-1, 1)
        dz = random_between(-1, 1)
        ray.set_direction(dx, dy, dz)

        rays.append(ray)

    rc = RayCluster(speed=343.0, time_step=1e-3)
    rc.rays = rays
    num_steps = 5
    for _ in range(num_steps):
        rc.forward()

    plot_objects(building, rc)
