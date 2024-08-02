from pathlib import Path

from building3d.logger import init_logger
from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.geom.point import Point
from building3d.simulators.rays.movie import make_movie
from building3d.simulators.rays.parallel_simulation import parallel_simulation
from building3d.io.b3d import write_b3d


if __name__ == "__main__":
    project_dir = "tmp/parallel/"
    main_logfile = Path(project_dir) / "main.log"
    init_logger(str(main_logfile))

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

    b3d_file = Path(project_dir) / "building.b3d"
    write_b3d(str(b3d_file), building)

    # Acoustic properties can be defined for each polygon/subpolygon separately
    # or in groups for parent objects (walls, solids, zones).
    # Group properties are propagated to all children objects.
    acoustic_properties = {
        "absorption": {
            "zone/solid_1/floor": 0.3,
            "zone/solid_1/wall-0/wall-0": 0.1,
            "zone/solid_1/wall-1": 0.1,
            "zone/solid_1/wall-2": 0.1,
            "zone/solid_1/wall-3": 0.1,
            "zone/solid_1/roof": 0.1,
            "zone/solid_2": 0.12,
            "zone/solid_3": 0.13,
            "zone/solid_4": 0.14,
        },
    }

    parallel_simulation(
        building = building,
        source = Point(1, 1, 1),
        sinks = [Point(3, 3, 2), Point(6, 6, 2)],
        sink_radius = 0.6,
        num_rays = 800,
        properties = acoustic_properties,
        sim_dir = project_dir,
        steps = 1500,
        num_jobs = 8,
    )
