import numpy as np

from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.geom.solid.floor_plan import floor_plan
from building3d.geom.zone import Zone
from building3d.sim.rays.simulation import Simulation
from building3d.sim.rays.config import SPEED, T_STEP
from building3d.display.plot_objects import plot_objects
from building3d.sim.rays.ray_buff_plotter import RayBuffPlotter


def test_ray_simulation(show=False):
    # Create building
    s = floor_plan(
        plan=[(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (0, 2)],
        height=1,
    )
    zone = Zone([s], "z")
    building = Building([zone], "b")

    # Sources and sinks
    source = np.array([1.5, 1.5, 0.5])
    sinks = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.1, 0.1, 0.6],
            [1.3, 1.3, 0.3],  # Close to the source to assure some ray hits it
        ]
    )

    # Number of rays should be sufficient to almost always pass this test
    num_rays = 100

    # Number of steps should be sufficient to travel between solids
    max_dist = 3.
    num_steps = int(max_dist / SPEED / T_STEP)

    sim = Simulation(building, source, sinks, num_rays, num_steps)
    pos_buf, vel_buf, enr_buf, hit_buf = sim.run()

    # At least some ray should be in solid_0
    assert (pos_buf[-1, :, 0] > 1).any()

    # At least some ray should be in solid_1
    assert (pos_buf[-1, :, 0] < 1).any()

    # At least some ray should bounce off a surface
    assert (enr_buf[:, :] < 1).any()

    # At least some ray should have different velocity at the beginning and the end
    assert (~np.isclose(vel_buf[0, :, :], vel_buf[-1, :, :])).any()

    # At least some ray should hit an absorber
    assert hit_buf.sum() > 0

    if show:
        rays = RayBuffPlotter(building, pos_buf, enr_buf)
        plot_objects((building, rays))


if __name__ == "__main__":
    test_ray_simulation(show=True)
