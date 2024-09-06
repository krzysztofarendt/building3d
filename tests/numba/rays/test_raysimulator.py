import os

import numpy as np

from building3d.geom.numba.building import Building
from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.points import new_point
from building3d.simulators.rays.numba.simulator import RaySimulator


def test_ray_simulator(plot=False):
    L = 1
    W = 1
    H = 1

    xlim = L
    ylim = W
    zlim = H
    s1 = box(xlim, ylim, zlim, name="s1")
    xlim = L
    ylim = W
    zlim = H
    s2 = box(xlim, ylim, zlim, (L, 0, 0), name="s2")
    xlim = L
    ylim = W
    zlim = H
    s3 = box(xlim, ylim, zlim, (L * 2, 0, 0), name="s3")
    # z = Zone([s1, s2, s3], "z")
    z = Zone([s1], "z")

    building = Building([z], "b")

    csv_file = "tmp/test_result.csv"
    if os.path.exists(csv_file):
        os.remove(csv_file)

    if plot:
        movie_path = "tmp/test_ray_simulator.mp4"
    else:
        movie_path = None

    raysim = RaySimulator(
        building=building,
        source=new_point(0.3, 0.3, 0.3),
        sinks=[new_point(0.6, 0.6, 0.6)],
        sink_radius=0.1,
        num_rays=10,
        csv_file=csv_file,
    )
    locations = [r.loc for r in raysim.rays]
    unique_locations = np.unique(locations)
    assert (
        len(unique_locations) == 1
    ), "Rays located in more than 1 solid at the beginning of simulation?"

    raysim.simulate(200)
    locations = [r.loc for r in raysim.rays]
    unique_locations = np.unique(locations)
    # assert (
    #     len(unique_locations) == 3
    # ), "Rays not in all three solids at the end of simulation?"

    # assert os.path.exists(csv_file)

    # if plot:
    #     assert isinstance(movie_path, str)
    #     assert os.path.exists(movie_path)
