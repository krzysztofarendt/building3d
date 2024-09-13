from numba import njit
import numpy as np

from building3d.io.arrayformat import to_array_format
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.types import PointType, IndexType


class Simulation:

    def __init__(
        self,
        building: Building,
        source: PointType,
        sinks: PointType,
        num_rays: int,
        num_steps: int,
    ):
        self.building = building
        self.source = source.copy()
        self.sinks = sinks.copy()
        self.num_rays = num_rays
        self.num_steps = num_steps

    def run(self):
        points, faces, polygons, walls, solids, zones = to_array_format(self.building)

        num_hits = simulation_loop(
            self.num_steps,
            self.num_rays,
            source = self.source,
            sinks = self.sinks,
            points = points,
            faces = faces,
            polygons = polygons,
            walls = walls,
            solids = solids,
            zones = zones,
        )

        return num_hits


@njit
def simulation_loop(
    # Simulation setup
    num_steps: int,
    num_rays: int,
    source: PointType,
    sinks: PointType,
    # Building in the array format
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    walls: IndexType,
    solids: IndexType,
    zones: IndexType,
):
    num_hits = 0

    # Simulation parameters (TODO: add to config and/or property dict)
    t_step = 1e-4
    absorption = 0.1
    sink_radius = 0.1

    # Initial energy
    energy = np.ones(num_rays)

    # Direction and velocity
    speed = 343.
    direction = np.random.rand(num_rays, 3) * 2.0 - 1.0
    velocity = direction * speed
    delta_pos = velocity * t_step

    # Initial position
    pos = np.zeros((num_rays, 3))
    for i in range(num_rays):
        pos[i, :] = source.copy()

    # Distance to each sink
    num_sinks = sinks.shape[0]
    sink_dist = np.zeros((num_sinks, num_rays))
    for sn in range(num_sinks):
        sink_dist[sn, :] = np.sqrt(np.sum((pos - sinks[sn])**2, axis=1))

    # Move rays
    for i in range(num_steps):
        pos += delta_pos

        # Check sinks
        for sn in range(num_sinks):
            sink_dist[sn, :] = np.sqrt(np.sum((pos - sinks[sn])**2, axis=1))

        hit = np.where(sink_dist < sink_radius, 1, 0)

        num_hits += np.sum(hit)

    return num_hits
