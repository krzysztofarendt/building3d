import logging
from pathlib import Path

from tqdm import tqdm

from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.manyrays import ManyRays
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
    - exporting simulation movie or gif
    """
    def __init__(
        self,
        building: Building,
        source: Point,
        receiver: Point,
        receiver_radius: float,
        num_rays: int = 1000,
        movie_file: None | str = None,
    ):
        logger.info("RaySimulator initialization...")

        self.building = building
        self.source = source
        self.receiver = receiver
        self.receiver_radius = receiver_radius

        self.num_step = 0

        self.rays = ManyRays(
            num_rays=num_rays,
            building=building,
            source=source,
        )

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
        """Overwrite the initial location for all rays to speed up the first step."""
        init_loc = get_location(self.source, self.building)
        for i in range(len(self.rays)):
            self.rays[i].location = init_loc

    def forward(self) -> None:
        """Process next simulation step."""
        logger.info(f"Processing time step {self.num_step}")

        if self.num_step == 0:
            self.set_initial_location()

        for i in range(len(self.rays)):
            logger.debug(f"Processing ray {i}: {self.rays[i]}")
            self.rays[i].forward()

        self.num_step += 1

        if self.movie is not None:
            self.movie.update()

    def simulate(self, steps: int) -> None:
        """Simulate chosen number of steps and save a movie.

        Args:
            steps: number of steps to simulate
        """
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
