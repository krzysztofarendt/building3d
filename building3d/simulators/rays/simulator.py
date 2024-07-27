import logging
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from building3d import random_between
from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.geom.vector import length
from building3d.geom.vector import vector
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.manyrays import ManyRays
from building3d.simulators.rays.ray import Ray
from .raymovie import RayMovie
from .find_location import find_location
from .ray import Ray


logger = logging.getLogger(__name__)


class RaySimulator(BaseSimulator):
    """Simulator class for ray tracing.

    Controls:
    - time steps
    - source and receiver
    - reflections
    - absorption
    - when to finish
    - exporting simulation movie or gif
    """
    def __init__(
        self,
        building: Building,
        source: Point,
        receiver: Point,
        receiver_radius: float,
        num_rays: int,
        properties: None | dict = None,
        csv_file: None | str = None,
        movie_file: None | str = None,
        state_dump_dir: None | str = None,
    ):
        logger.info("RaySimulator initialization...")

        self.building = building
        self.source = source
        self.receiver = receiver
        self.receiver_radius = receiver_radius
        self.received_energy = np.zeros(1)  # placeholder, reinitialized in self.simulate()

        self.num_step = 0

        self.rays = ManyRays(
            num_rays=num_rays,
            building=building,
            source=source,
            properties=properties,
        )
        self.total_energy = sum([self.rays[i].energy for i in range(len(self.rays))])
        self.num_active_rays = len(self.rays)

        # Make parent dir for CSV file
        if csv_file is not None:
            parent_dir = Path(csv_file).parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True)
            self.csv_file = csv_file
        else:
            logger.warning("No output CSV file specified. Receiver results will not be saved!")
            self.csv_file = None

        # Make parent dir for output movie (or gif)
        if movie_file is not None:
            parent_dir = Path(movie_file).parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True)
            self.movie = RayMovie(filename=movie_file, building=building, rays=self.rays)
        else:
            self.movie = None

        self.state_dump_dir = state_dump_dir

    def set_initial_location(self):
        """Overwrite the initial location for all rays to speed up the first step."""
        init_loc = find_location(self.source, self.building)
        for i in range(len(self.rays)):
            self.rays[i].location = init_loc

    def set_initial_direction(self):
        """Set initial, random direction to all rays."""
        for i in range(len(self.rays)):
            self.rays[i].set_direction(
                dx = random_between(-1, 1),  # TODO: direction within xlim possible
                dy = random_between(-1, 1),  # TODO: direction within ylim possible
                dz = random_between(-1, 1),  # TODO: direction within zlim possible
            )

    def forward(self) -> None:
        """Process next simulation step."""
        logger.info(
            f"Simulation step {self.num_step}, "
            f"total energy = {self.total_energy:.2f}, "
            f"active rays = {self.num_active_rays}"
        )

        self.total_energy = 0
        self.num_active_rays = 0

        if self.num_step == 0:
            self.set_initial_location()
            self.set_initial_direction()  # currently, omnidirectional source

        for i in range(len(self.rays)):
            logger.debug(f"Processing ray {i}: {self.rays[i]}")

            if self.rays[i].energy > 0:
                self.rays[i].forward()

                if RaySimulator.is_hit(self.rays[i], self.receiver, self.receiver_radius):
                    self.received_energy[self.num_step] += self.rays[i].energy
                    self.rays[i].energy = 0
                    logger.debug(f"Ray hits receiver: {self.rays[i]}")

                self.total_energy += self.rays[i].energy
                self.num_active_rays += 1

        self.num_step += 1

        if self.movie is not None:
            self.movie.update()

    def simulate(self, steps: int) -> None:
        """Simulate chosen number of steps and save a movie.

        Args:
            steps: number of steps to simulate
        """
        self.received_energy = np.zeros(steps)

        logger.info("Starting the simulation")
        print("Simulation started")
        for i in tqdm(range(steps)):
            if self.state_dump_dir is not None:
                self.rays.dump_state(self.state_dump_dir, i)
            self.forward()

        if self.state_dump_dir is not None:
            self.rays.dump_state(self.state_dump_dir, steps - 1)

        logger.info("Simulation finished")
        print("Simulation finished")

        if self.csv_file is not None:
            self.save_results()

        if self.movie is not None:
            self.movie.save()

    def save_results(self):
        df = pd.DataFrame(
            index=pd.Index(np.arange(0, self.num_step) * Ray.time_step, name="time"),
        )
        df["received_energy"] = self.received_energy
        df.to_csv(self.csv_file)

    @staticmethod
    def is_hit(ray: Ray, receiver: Point, radius: float) -> bool:
        if length(vector(ray.position, receiver)) < radius:
            return True
        else:
            return False

    def is_finished(self):  # TODO: Needed?
        return False
