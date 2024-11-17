import os
from tempfile import TemporaryDirectory

from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.geom.solid.floor_plan import floor_plan
from building3d.geom.zone import Zone
from building3d.sim.rays.simulation import Simulation
from building3d.display.plot_objects import plot_objects
from building3d.sim.rays.ray_buff_plotter import RayBuffPlotter
from building3d.sim.rays.simulation_config import SimulationConfig


def test_ray_simulation(show=False):
    with TemporaryDirectory() as tempdir:
        # Create building
        s = floor_plan(
            plan=[(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (0, 2)],
            height=1,
        )
        zone = Zone([s], "z")
        building = Building([zone], "b")

        # Simulation configuration
        sim_cfg = SimulationConfig(building)

        # Overwrite defaults
        num_rays = 100
        time_step = 1e-4
        speed = 343.0
        max_dist = 3.0  # Distance we want the rays to travel
        num_steps = int(max_dist / speed / time_step)

        sim_cfg.paths["project_dir"] = tempdir
        sim_cfg.paths["buffer_dir"] = os.path.join(tempdir, "states")
        sim_cfg.engine["time_step"] = time_step
        sim_cfg.engine["num_steps"] = num_steps
        sim_cfg.engine["batch_size"] = num_steps
        sim_cfg.rays["ray_speed"] = speed
        sim_cfg.rays["num_rays"] = num_rays
        sim_cfg.rays["source"] = (1.5, 1.5, 0.5)
        sim_cfg.rays["absorbers"] = [
            (0.0, 0.0, 0.0),
            (0.1, 0.1, 0.6),
            (1.3, 1.3, 0.3),  # Close to the source to assure some ray hits it
        ]

        # Run simulation
        sim = Simulation(building, sim_cfg)
        pos_buf, enr_buf, hit_buf = sim.run()

        # At least some ray should be in solid_0
        assert (pos_buf[-1, :, 0] > 1).any()

        # At least some ray should be in solid_1
        assert (pos_buf[-1, :, 0] < 1).any()

        # At least some ray should bounce off a surface
        assert (enr_buf[:, :] < 1).any()

        # At least some ray should hit an absorber
        assert hit_buf.sum() > 0

        if show:
            rays = RayBuffPlotter(building, pos_buf, enr_buf)
            plot_objects((building, rays))


if __name__ == "__main__":
    test_ray_simulation(show=True)
