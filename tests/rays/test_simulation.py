import numpy as np

from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.solid import Solid
from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.sim.rays.simulation import Simulation
from building3d.sim.rays.config import SPEED, T_STEP


def test_ray_simulation():
    # Need to reset the counters before using the array format functions
    Polygon.count = 0
    Wall.count = 0
    Solid.count = 0
    Zone.count = 0
    Building.count = 0

    # Create building
    solid_0 = box(1, 1, 1, (0, 0, 0), "s0")
    solid_1 = box(1, 1, 1, (1, 0, 0), "s1")
    zone = Zone([solid_0, solid_1], "z")
    building = Building([zone], "b")

    # Sources and sinks
    source = np.array([0.5, 0.5, 0.5])
    sinks = np.array(
        [
            [0.8, 0.8, 0.8],
            [0.1, 0.1, 0.1],
        ]
    )

    # Number of rays should be sufficient to almost always pass this test
    num_rays = 100

    # Number of steps should be sufficient to travel from solid_0 to solid_1
    max_dist = 1.5
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

    # At least some ray should hit the sink
    assert hit_buf.sum() > 0
