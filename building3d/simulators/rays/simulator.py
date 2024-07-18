import numpy as np
from tqdm import tqdm

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d import random_between
from building3d.geom.point import Point
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.ray import Ray
from building3d.simulators.rays.manyrays import ManyRays
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.object_path import split_path


class RaySimulator(BaseSimulator):
    """Simulator class for ray tracing.

    Controls:
    - time steps
    - source and receiver
    - reflections
    - absorption
    - when to finish
    """
    def __init__(
        self,
        building: Building,
        source: Point,
        receiver: Point,
        receiver_radius: float,
        num_rays: int = 1000,
        speed: float = 343.0,
        time_step: float = 1e-4,
    ):
        self.building = building
        self.building_adj_polygons = building.get_graph()
        self.building_adj_solids = building.find_adjacent_solids()

        self.source = source
        self.receiver = receiver
        self.receiver_radius = receiver_radius
        self.speed = speed
        self.time_step = time_step
        self.min_distance = speed * time_step * 1.01

        self.rays = ManyRays(
            building=building,
            source=source,
            speed=speed,
            time_step=time_step,
        )
        self.rays.add_rays(num_rays=num_rays)
        self.lag = np.zeros(len(self.rays), dtype=np.uint8)

        # Initialize rays: find enclosing solid, find next surface for each ray
        self.rays.init_location()

        print("Finding next surface for each ray...")
        for i in tqdm(range(len(self.rays))):
            self.rays[i].update_location_and_target_surface()

        # TODO:
        # - Decide if properties (transparency, absorption, scattering)
        #   should be stored here or in Wall
        # - Decide if subpolygons are of any use here
        ...

    def forward(self):
        # If distance below threshold, reflect (change direction)
        max_allowed_lags = 10

        for i in range(len(self.rays)):

            if self.rays[i].dist is None:
                self.rays[i].update_distance()

            d = self.rays[i].dist

            # Schedule at least 1 step forward
            self.lag[i] += 1

            # Move forward until lag is reduced to 0
            # (there may be additional lag when the ray is reflected near a corner
            #  and can't immediately move, because it would go outside the building)
            while self.lag[i] > 0:
                if d <= self.min_distance:
                    # TODO: Consider transparent surfaces
                    #       - pass through
                    #       - update location
                    # Reflect
                    poly = self.building.get_object(self.rays[i].target_surface)
                    assert isinstance(poly, Polygon)
                    self.rays[i].reflect(poly.normal)
                    self.rays[i].update_location_and_target_surface()

                    # Check if can move forward
                    # (don't if there is a risk of landing on the other side of the surface)
                    self.rays[i].update_distance()
                    d = self.rays[i].dist
                    if d < self.min_distance:
                        # Remember that this ray is 1 step behind due to corner reflection.
                        # This lag will have to be reduced by moving forward multiple times.
                        self.lag[i] += 1
                        continue

                    if self.lag[i] >= max_allowed_lags:
                        raise RuntimeError("Too many reflections caused too high ray lag")

                # Move rays forward
                self.rays[i].forward()
                self.lag[i] -= 1

    def simulate(self, steps: int):
        print("Simulation...")
        for _ in tqdm(range(steps)):
            self.forward()

    def is_finished(self):
        return False
