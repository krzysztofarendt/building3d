import os
import time

import numpy as np

from building3d.logger import init_logger
from building3d.io.stl import read_stl
from building3d.display.plot_objects import plot_objects
from building3d.io.b3d import write_b3d
from building3d.simulators.rays_numba.simulation import Simulation
from building3d.simulators.rays_numba.ray_buff_plotter import RayBuffPlotter
from building3d.simulators.rays_numba.movie_from_buffer import make_movie_from_buffer


if __name__ == "__main__":
    # Parameters
    project_dir = "tmp"

    main_logfile = os.path.join(project_dir, "log")
    init_logger(main_logfile)

    # Create building
    building = read_stl("resources/utah_teapot.stl")

    # Sources and sinks
    source = np.array([3.0, 3.0, 3.0])
    sinks = np.array([
        [4.0, 4.0, 4.0],
    ])

    # Rays
    num_rays = 20000
    num_steps = 1000
    # num_rays = 50
    # num_steps = 1000

    sim = Simulation(building, source, sinks, num_rays, num_steps, search_transparent=False)
    t0 = time.time()
    pos_buf, vel_buf, enr_buf, hit_buf = sim.run()  # TODO: Some rays go outside the teapot
    tot_time = time.time() - t0
    print(f"{tot_time=:.2f}")

    # Save building
    b3d_file = os.path.join(project_dir, "building.b3d")
    write_b3d(b3d_file, building)

    # Save results
    # dump_buffers(pos_buf, vel_buf, enr_buf, hit_buf, "tmp")  # TODO: Refactor

    # Show plot
    # rays = RayBuffPlotter(building, pos_buf, enr_buf)
    # plot_objects((building, rays))

    make_movie_from_buffer(
        output_file="movie.mp4",
        building=building,
        pos_buf=pos_buf,
        enr_buf=enr_buf,
    )
