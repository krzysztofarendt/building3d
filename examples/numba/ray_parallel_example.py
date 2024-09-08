import os
from pathlib import Path

from building3d.logger import init_logger
from building3d.geom.numba.building import Building
from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.points import new_point
from building3d.simulators.rays.numba.movie import make_movie
from building3d.simulators.rays.numba.parallel_simulation import parallel_simulation
from building3d.simulators.rays.numba.config import MAIN_LOG_FILE
from building3d.io.numba.b3d import write_b3d


if __name__ == "__main__":
    project_dir = "tmp/parallel/"
    main_logfile = os.path.join(project_dir, MAIN_LOG_FILE)
    init_logger(main_logfile)

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
    zone = Zone([solid_1, solid_2, solid_3, solid_4], "zone")

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
        building=building,
        source=new_point(1, 1, 1),
        sinks=[new_point(3, 3, 2), new_point(6, 6, 2)],
        sink_radius=0.6,
        num_rays=16000,
        properties=acoustic_properties,
        sim_dir=project_dir,
        steps=1000,
        num_jobs=8,
    )
