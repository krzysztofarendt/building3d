import os
import time

import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.io.b3d import write_b3d
from building3d.io.stl import read_stl
from building3d.logger import init_logger
from building3d.simulators.rays.movie_from_buffer import make_movie_from_buffer
from building3d.simulators.rays.ray_buff_plotter import RayBuffPlotter
from building3d.simulators.rays.simulation import Simulation

if __name__ == "__main__":
    # Parameters
    output_dir = "out/ray_sphere_example"

    main_logfile = os.path.join(output_dir, "log")
    init_logger(main_logfile)

    # Create building
    building = read_stl("resources/sphere.stl")

    # Sources and sinks
    source = np.array([0.5, 0.0, 0.0])
    sinks = np.array(
        [
            [-0.5, 0.0, 0.0],
        ]
    )

    # Rays
    num_rays = 1000
    num_steps = 500

    sim = Simulation(
        building, source, sinks, num_rays, num_steps, search_transparent=False
    )
    t0 = time.time()
    pos_buf, vel_buf, enr_buf, hit_buf = (
        sim.run()
    )  # TODO: Some rays go outside the teapot
    tot_time = time.time() - t0
    print(f"{tot_time=:.2f}")

    # Save building
    b3d_file = os.path.join(output_dir, "building.b3d")
    write_b3d(b3d_file, building)

    # Show plot
    rays = RayBuffPlotter(building, pos_buf, enr_buf)
    plot_objects((building, rays))

    make_movie_from_buffer(
        output_file=f"{output_dir}/movie.mp4",
        building=building,
        pos_buf=pos_buf,
        enr_buf=enr_buf,
    )
