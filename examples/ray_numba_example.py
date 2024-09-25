import time

import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.simulators.rays_numba.simulation import Simulation


if __name__ == "__main__":
    # Create building
    solid_0 = box(1, 1, 1, (0, 0, 0), "s0")
    solid_1 = box(1, 1, 1, (1, 0, 0), "s1")
    zone = Zone([solid_0, solid_1], "z")
    building = Building([zone], "b")

    # Sources and sinks
    source = np.array([0.3, 0.3, 0.3])
    sinks = np.array([
        [0.6, 0.6, 0.6],
        [0.1, 0.1, 0.6],
    ])

    # Rays
    num_rays = 5
    num_steps = 30

    sim = Simulation(building, source, sinks, num_rays, num_steps)
    t0 = time.time()
    sim.run()
    tot_time = time.time() - t0
    print(f"{tot_time=:.2f}")
