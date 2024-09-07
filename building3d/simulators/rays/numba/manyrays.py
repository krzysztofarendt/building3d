import os
import logging

import numpy as np

from building3d import random_between
from building3d.geom.numba.types import PointType, IndexType, FLOAT, INT
from building3d.geom.numba.building import Building
from building3d.geom.numba.building.find_location import find_location
from building3d.paths.wildcardpath import WildcardPath
from .ray import Ray
from .config import ENERGY_FILE, POSITION_FILE


logger = logging.getLogger(__name__)


class ManyRays:
    """Collection of `Ray` instances located in a `Building`."""

    def __init__(
        self,
        num_rays: int,
        source: PointType,
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
        """Save ray positions and energy to files. Used e.g. for movie generation."""
        logger.debug(f"Saving state of {self} to {dump_dir}")

        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)

        position = np.array(
            [self.rays[i].pos for i in range(len(self.rays))]
        )
        energy = np.array(self.get_energy())

        position_file = WildcardPath(POSITION_FILE).fill(parent=dump_dir, step=step)
        energy_file = WildcardPath(ENERGY_FILE).fill(parent=dump_dir, step=step)

        np.save(position_file, position)
        np.save(energy_file, energy)

    def get_lines(self) -> tuple[PointType, IndexType]:
        """Interface to building3d.display.plot_objects.plot_objects()"""
        line_len = Ray.buff_size

        verts = []
        lines = []
        curr_index = 0
        for r in self.rays:
            verts.extend(list(r.past_pos))
            lines.append([curr_index + i for i in range(line_len)])
            curr_index += line_len

        return np.vstack(verts, dtype=FLOAT), np.vstack(lines)  # TODO: missing dtype for lines

    def get_points(self) -> PointType:
        """Interface to building3d.display.plot_objects.plot_objects()"""
        return np.vstack([r.pos for r in self.rays])

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
