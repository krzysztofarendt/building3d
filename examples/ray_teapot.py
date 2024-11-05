import os
import time

from building3d.display.plot_objects import plot_objects
from building3d.io.b3d import write_b3d
from building3d.io.stl import read_stl
from building3d.logger import init_logger
from building3d.sim.rays.movie_from_buffer import make_movie_from_buffer
from building3d.sim.rays.ray_buff_plotter import RayBuffPlotter
from building3d.sim.rays.simulation import Simulation
from building3d.sim.rays.simulation_config import SimulationConfig

if __name__ == "__main__":
    # Parameters
    output_dir = "out/ray_teapot"

    main_logfile = os.path.join(output_dir, "log")
    init_logger(main_logfile)

    # Create building
    building = read_stl("resources/utah_teapot.stl")

    # Simulation configuration
    sim_cfg = SimulationConfig(building)

    sim_cfg.engine["num_steps"] = 700
    sim_cfg.engine["buffer_size"] = 700
    sim_cfg.rays["num_rays"] = 5000  # It looks nice with 50k rays
    sim_cfg.rays["source"] = (0.0, 0.0, 8.0)
    sim_cfg.rays["absorbers"] = [[0.0, 0.0, 4.0]]
    sim_cfg.surfaces["absorption"]["default"] = 0.1
    sim_cfg.engine["voxel_size"] = 0.25
    sim_cfg.engine["search_transparent"] = False  # Because it is very slow for this model
    sim_cfg.visualization["ray_opacity"] = 0.1
    sim_cfg.visualization["ray_trail_opacity"] = 0.1


    # Simulate
    sim = Simulation(building, sim_cfg)
    t0 = time.time()
    pos_buf, vel_buf, enr_buf, hit_buf = sim.run()

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
        sim_cfg=sim_cfg,
    )