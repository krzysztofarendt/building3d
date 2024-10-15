import os
import time

import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.io.b3d import write_b3d
from building3d.simulators.rays_numba.dump_buffers import dump_buffers
from building3d.simulators.rays_numba.dump_buffers import read_buffers
from building3d.simulators.rays_numba.movie_from_buffer import \
    make_movie_from_buffer
from building3d.simulators.rays_numba.ray_buff_plotter import RayBuffPlotter
from building3d.simulators.rays_numba.simulation import Simulation

if __name__ == "__main__":
    # Parameters
    project_dir = "tmp"

    # Create building
    solid_0 = box(1, 1, 1, (0, 0, 0), "s0")
    # solid_1 = box(1, 1, 1, (1, 0, 0), "s1")
    # zone = Zone([solid_0, solid_1], "z")
    zone = Zone([solid_0], "z")
    building = Building([zone], "b")

    # Sources and sinks
    source = np.array([0.3, 0.3, 0.3])
    sinks = np.array(
        [
            [0.6, 0.6, 0.6],
            [0.1, 0.1, 0.6],
        ]
    )

    # Rays
    num_rays = 500
    num_steps = 1000

    sim = Simulation(building, source, sinks, num_rays, num_steps)
    t0 = time.time()
    pos_buf, vel_buf, enr_buf, hit_buf = sim.run()
    tot_time = time.time() - t0
    print(f"{tot_time=:.2f}")

    # Save building
    b3d_file = os.path.join(project_dir, "building.b3d")
    write_b3d(b3d_file, building)

    # Save and read buffers - if the video looks fine, these functions work OK
    dump_buffers(pos_buf, vel_buf, enr_buf, hit_buf, "tmp")
    pos_buf, vel_buf, enr_buf, hit_buf = read_buffers("tmp")

    # Show plot
    rays = RayBuffPlotter(building, pos_buf, enr_buf)
    plot_objects((building, rays))

    make_movie_from_buffer(
        output_file="movie.mp4",
        building=building,
        pos_buf=pos_buf,
        enr_buf=enr_buf,
    )
