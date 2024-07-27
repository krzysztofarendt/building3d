import logging
from pathlib import Path

import numpy as np

from building3d.geom.point import Point
from building3d.geom.building import Building
from .ray import Ray


logger = logging.getLogger(__name__)


class ManyRays:
    """Collection of `Ray` instances located in a `Building`.
    """
    def __init__(
        self,
        num_rays: int,
        source: Point,
        building: Building,
        properties: None | dict = None,
    ):
        logger.debug("ManyRays initialization")

        self.source = source
        self.rays: list[Ray] = []

        for _ in range(num_rays):
            r = Ray(position=source, building=building, properties=properties)
            self.rays.append(r)

    def get_energy(self) -> list[float]:
        return [self.rays[i].energy for i in range(len(self.rays))]

    def dump_state(self, dump_dir: str, step: int):
        logger.debug(f"Saving state of {self} to {dump_dir}")

        d_dir = Path(dump_dir)
        if not d_dir.exists():
            d_dir.mkdir(parents=True)

        position = np.array([self.rays[i].position.vector() for i in range(len(self.rays))])
        energy = np.array(self.get_energy())

        position_file = Path(d_dir) / f"position_{step}.npy"
        energy_file = Path(d_dir) / f"energy_{step}.npy"

        np.save(position_file, position)
        np.save(energy_file, energy)

    def get_lines(self) -> tuple[list[Point], list[list[int]]]:
        """Interface to building3d.display.plot_objects.plot_objects()"""
        line_len = Ray.buffer_size

        verts = []
        lines = []
        curr_index = 0
        for r in self.rays:
            verts.extend(list(r.past_positions))
            lines.append([curr_index + i for i in range(line_len)])
            curr_index += line_len

        return verts, lines

    def get_points(self) -> list[Point]:
        """Interface to building3d.display.plot_objects.plot_objects()"""
        return [r.position for r in self.rays]

    def __len__(self):
        return len(self.rays)

    def __getitem__(self, key: int) -> Ray:
        if not isinstance(key, int):
            raise TypeError(f"Incorrect key type: {type(key)} (should be int)")
        return self.rays[key]

    def __setitem__(self, key: int, value: Ray) -> None:
        if not isinstance(key, int):
            raise TypeError(f"Incorrect key type: {type(key)} (should be int)")
        if not isinstance(value, Ray):
            raise TypeError(f"Incorrect value type: {type(key)} (should be Ray)")
        self.rays[key] = value

    def __str__(self):
        s = f"ManyRays(num_rays={len(self.rays)}, source={self.source}, id={hex(id(self))})"
        return s
