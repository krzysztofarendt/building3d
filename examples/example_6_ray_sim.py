import building3d.logger
from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.geom.point import Point
from building3d.simulators.rays.simulator import RaySimulator
from building3d.simulators.rays.movie import make_movie
from building3d.io.b3d import write_b3d


if __name__ == "__main__":
    L = 4
    W = 4
    H = 4

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
    ylim = W
    zlim = H
    solid_4 = box(xlim, ylim, zlim, (L, W, 0), name="solid_4")
    zone = Zone("zone")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)
    zone.add_solid(solid_3)
    zone.add_solid(solid_4)

    building = Building(name="building")
    building.add_zone(zone)

    b3d_file = "tmp/building.b3d"
    write_b3d(b3d_file, building)

    # Acoustic properties can be defined for each polygon/subpolygon separately
    # or in groups for parent objects (walls, solids, zones).
    # Group properties are propagated to all children objects.
    acoustic_properties = {
        "absorption": {
            "zone/solid_1/floor": 0.1,
            "zone/solid_1/wall-0/wall-0": 0.2,
            "zone/solid_1/wall-1": 0.2,
            "zone/solid_1/wall-2": 0.2,
            "zone/solid_1/wall-3": 0.2,
            "zone/solid_1/roof": 0.2,
            "zone/solid_2": 0.3,
            "zone/solid_3": 0.4,
            "zone/solid_4": 0.5,
        },
    }

    state_dump_dir = "tmp/state_dump/"

    raysim = RaySimulator(
        building = building,
        source = Point(1, 1, 1),
        receiver = Point(6, 6, 2),
        receiver_radius = 0.3,
        num_rays = 25000,
        properties = acoustic_properties,
        csv_file="tmp/results.csv",
        state_dump_dir = state_dump_dir,
    )
    raysim.simulate(1000)
    plot_objects((building, raysim.rays), output_file="tmp/ray_simulation_last_state.png")

    print("Making movie")
    movie_file = "tmp/ray_simulation.mp4"  # .gif or .mp4
    make_movie(movie_file, state_dump_dir, b3d_file, 300)

