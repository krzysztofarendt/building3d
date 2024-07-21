import building3d.logger
from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.geom.point import Point
from building3d.simulators.rays.simulator import RaySimulator


if __name__ == "__main__":
    L = 2
    W = 2
    H = 2

    xlim = L
    ylim = W
    zlim = H
    solid_1 = box(xlim, ylim, zlim, name="solid_1")
    xlim = L
    ylim = W
    zlim = H
    solid_2 = box(xlim, ylim, zlim, (L, 0, 0), name="solid_2")
    xlim = L
    ylim = W
    zlim = H
    solid_3 = box(xlim, ylim, zlim, (L * 2, 0, 0), name="solid_3")
    xlim = L
    ylim = 3 * W
    zlim = H
    solid_4 = box(xlim, ylim, zlim, (L, W, 0), name="solid_4")
    zone = Zone("zone")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)
    zone.add_solid(solid_3)
    zone.add_solid(solid_4)

    building = Building(name="building")
    building.add_zone(zone)

    raysim = RaySimulator(
        building = building,
        source = Point(1, 1, 1),
        receiver = Point(3, 3, 2),
        receiver_radius = 1,
        num_rays = 1000,
        movie_file = "tmp/ray_simulation.mp4",  # .gif or .mp4
    )
    raysim.simulate(250)

    plot_objects((building, raysim.rays), output_file="tmp/ray_simulation_last_state.png")
