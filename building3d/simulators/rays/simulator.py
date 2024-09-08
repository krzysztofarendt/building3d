import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd

from building3d import random_between
from building3d.logger import init_logger
from building3d.geom.building import Building
from building3d.geom.types import PointType
from building3d.geom.points import point_to_tuple
from building3d.simulators.rays.manyrays import ManyRays
from building3d.simulators.rays.ray import Ray
from building3d.geom.building.find_location import find_location


logger = logging.getLogger(__name__)


def simulation_job(
    building: Building,
    source: PointType,
    sinks: list[PointType],
    sink_radius: float,
    num_rays: int,
    properties: None | dict,
    csv_file: None | str,
    state_dump_dir: None | str,
    steps: int,
    logfile: None | str,
) -> None:

    init_logger(
        logfile
    )  # TODO: Each process has a separate log file. Should it stay like this?

    raysim = RaySimulator(
        building=building,
        source=source,
        sinks=sinks,
        sink_radius=sink_radius,
        num_rays=num_rays,
        properties=properties,
        csv_file=csv_file,
        state_dump_dir=state_dump_dir,
    )
    raysim.simulate(steps)


class RaySimulator:
    """Simulator class for ray tracing.

    Controls:
    - time steps
    - one source and one or more sinks
    - reflections
    - absorption
    - when to finish
    """

    def __init__(
        self,
        building: Building,
        source: PointType,
        sinks: list[PointType],
        sink_radius: float,
        num_rays: int,
        properties: None | dict = None,
        csv_file: None | str = None,
        state_dump_dir: None | str = None,
    ):
        logger.info("RaySimulator initialization...")

        self.building = building
        self.source = source.copy()
        self.sinks = [s.copy() for s in sinks]
        self.sink_radius = sink_radius

        self.num_steps = 0
        self.step = 0

        self.rays = ManyRays(
            num_rays=num_rays,
            building=building,
            source=source,
            properties=properties,
        )
        self.total_energy = sum([self.rays[i].energy for i in range(len(self.rays))])
        self.num_active_rays = len(self.rays)
        self.hits = {}

        # Make parent dir for CSV file
        if csv_file is not None:
            parent_dir = Path(csv_file).parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True)
            self.csv_file = csv_file
        else:
            logger.warning(
                "No output CSV file specified. Receiver results will not be saved!"
            )
            self.csv_file = None

        self.state_dump_dir = state_dump_dir

    def initialize(self) -> None:
        init_loc = find_location(self.source, self.building)

        for i in range(len(self.rays)):
            self.rays[i].set_direction(
                dx=random_between(-1, 1),  # TODO: direction within xlim possible
                dy=random_between(-1, 1),  # TODO: direction within ylim possible
                dz=random_between(-1, 1),  # TODO: direction within zlim possible
            )
            self.rays[i].loc = init_loc
            self.rays[i].update_target_surface()
            self.rays[i].update_distance(fast_calc=False)

    def simulate(self, steps: int) -> None:
        """Simulate chosen number of steps.

        Args:
            steps: number of steps to simulate
        """
        logger.info(f"Simulation started (pid = {os.getpid()})")
        print(f"Simulation started (pid = {os.getpid()})")

        self.num_steps = steps

        self.initialize()

        for i in range(steps):
            if self.state_dump_dir is not None:
                self.rays.dump_state(self.state_dump_dir, i)
            self.forward()

        if self.state_dump_dir is not None:
            self.rays.dump_state(self.state_dump_dir, steps - 1)

        logger.info(f"Simulation finished (pid = {os.getpid()})")
        print(f"Simulation finished (pid = {os.getpid()})")

        if self.csv_file is not None:
            self.save_results()

    def forward(self) -> None:
        """Process next simulation step."""
        logger.info(
            f"Simulation step {self.step}, "
            f"total energy = {self.total_energy:.2f}, "
            f"active rays = {self.num_active_rays}"
        )

        self.total_energy = 0
        self.num_active_rays = 0

        for i in range(len(self.rays)):
            logger.debug(f"Processing ray {i}: {self.rays[i]}")

            if self.rays[i].energy > 0:
                self.rays[i].forward()

                for sink in self.sinks:
                    hit = self.check_hit(
                        self.rays[i], sink, self.sink_radius, self.step
                    )
                    if hit:
                        self.rays[i].energy = 0
                        break

                self.total_energy += self.rays[i].energy
                self.num_active_rays += 1

        self.step += 1

    def save_results(self):
        df = pd.DataFrame(
            index=pd.Index(np.arange(0, self.step) * Ray.time_step, name="time"),
        )
        for i, sink in enumerate(self.sinks):
            df[i] = self.hits[point_to_tuple(sink)]
        df.to_csv(self.csv_file)

    def check_hit(self, ray: Ray, sink: PointType, radius: float, step: int) -> bool:
        sink_tuple = point_to_tuple(sink)
        if sink_tuple not in self.hits:
            self.hits[sink_tuple] = np.zeros(self.num_steps)
        if np.linalg.norm(sink - ray.pos) < radius:
            self.hits[sink_tuple][step] += ray.energy
            return True
        else:
            return False
