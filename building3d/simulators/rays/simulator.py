import logging
from pathlib import Path

import numpy as np
from tqdm import tqdm

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.point import Point
from building3d.geom.paths.object_path import object_path
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.manyrays import ManyRays
from .find_transparent import find_transparent
from .raymovie import RayMovie
from .get_location import get_location


logger = logging.getLogger(__name__)


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
        movie_file: None | str = None,
    ):
        logger.info("RaySimulator initialization...")

        self.building = building
        self.building_adj_polygons = building.get_graph()
        self.building_adj_solids = building.find_adjacent_solids()
        self.transparent_surfs = find_transparent(building)

        self.source = source
        self.receiver = receiver
        self.receiver_radius = receiver_radius
        self.speed = speed
        self.time_step = time_step
        self.min_distance = speed * time_step * 1.1

        self.num_step = 0

        self.rays = ManyRays(
            num_rays=num_rays,
            building=building,
            source=source,
        )
        self.lag = np.zeros(len(self.rays), dtype=np.uint8)

        # TODO:
        # - Decide if properties (transparency, absorption, scattering)
        #   should be stored here or in Wall
        # - Decide if subpolygons are of any use here
        ...

        if movie_file is not None:
            parent_dir = Path(movie_file).parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True)
            self.movie = RayMovie(filename=movie_file, building=building, rays=self.rays)
        else:
            self.movie = None

    def set_initial_location(self):
        init_loc = get_location(self.source, self.building)
        for i in range(len(self.rays)):
            self.rays[i].location = init_loc

    def forward(self):
        logger.info(f"Processing time step {self.num_step}")

        # If distance below threshold, reflect (change direction)
        max_allowed_lags = 10

        if self.num_step == 0:
            self.set_initial_location()

        for i in range(len(self.rays)):
            logger.debug(f"Process ray {i}: {self.rays[i]}")
            if self.num_step == 0:
                self.rays[i].update_target_surface()
                self.rays[i].update_distance()

            d = self.rays[i].dist

            # Schedule at least 1 step forward
            self.lag[i] = 1

            # Move forward until lag is reduced to 0
            # (there may be additional lag when the ray is reflected near a corner
            #  and can't immediately move, because it would go outside the building)
            while self.lag[i] > 0:
                if d <= self.min_distance:
                    logger.debug(f"Ray {i} needs to be reflected: {self.rays[i]}")

                    target_surface_name = self.rays[i].target_surface
                    assert target_surface_name not in self.transparent_surfs

                    # Reflect
                    poly = self.building.get_object(target_surface_name)
                    assert isinstance(poly, Polygon)
                    self.rays[i].reflect(poly.normal)
                    self.rays[i].update_location()
                    self.rays[i].update_target_surface()
                    self.rays[i].update_distance()

                    # Check if can move forward
                    # (don't if there is a risk of landing on the other side of the surface)
                    d = self.rays[i].dist
                    if d <= self.min_distance:
                        logger.debug(f"Ray {i} too close the surface to move forward: {self.rays[i]}")

                        # Remember that this ray is 1 step behind due to corner reflection.
                        # This lag will have to be reduced by moving forward multiple times.
                        self.lag[i] += 1
                        continue

                    if self.lag[i] >= max_allowed_lags:
                        raise RuntimeError("Too many reflections caused too high ray lag")

                # Move rays forward
                logger.debug(f"Moving ray {i} forward")
                self.rays[i].forward()
                self.rays[i].update_distance()
                self.lag[i] -= 1

        self.num_step += 1

        if self.movie is not None:
            self.movie.update()

    def simulate(self, steps: int):
        logger.info("Starting the simulation")
        print("Simulation started")
        for _ in tqdm(range(steps)):
            self.forward()

        logger.info("Simulation finished")
        print("Simulation finished")

        if self.movie is not None:
            self.movie.save()

    def is_finished(self):  # TODO: Needed?
        return False
