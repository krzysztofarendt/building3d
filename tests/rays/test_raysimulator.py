import os

import numpy as np

from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.geom.point import Point
from building3d.simulators.rays.simulator import RaySimulator


def test_ray_simulator(plot=False):
    L = 1
    W = 1
    H = 1

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
    zone = Zone("zone")
    zone.add_solid(solid_1)
    zone.add_solid(solid_2)
    zone.add_solid(solid_3)

    building = Building(name="building")
    building.add_zone(zone)

    csv_file = "tmp/test_result.csv"
    if os.path.exists(csv_file):
        os.remove(csv_file)

    if plot:
        movie_path = "tmp/test_ray_simulator.mp4"
    else:
        movie_path = None

    raysim = RaySimulator(
        building = building,
        source = Point(0.3, 0.3, 0.3),
        sinks = [Point(0.6, 0.6, 0.6)],
        sink_radius = 0.1,
        num_rays = 100,
        csv_file = csv_file,
    )
    locations = [r.location for r in raysim.rays]
    unique_locations = np.unique(locations)
    assert len(unique_locations) == 1, \
        "Rays located in more than 1 solid at the beginning of simulation?"

    raysim.simulate(100)
    locations = [r.location for r in raysim.rays]
    unique_locations = np.unique(locations)
    assert len(unique_locations) == 3, \
        "Rays not in all three solids at the end of simulation?"

    assert os.path.exists(csv_file)

    if plot:
        assert isinstance(movie_path, str)
        assert os.path.exists(movie_path)
