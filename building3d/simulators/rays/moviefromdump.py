import logging
from pathlib import Path

import numpy as np

from building3d.simulators.rays.ray import Ray


logger = logging.getLogger(__name__)


class MovieFromDump:

    energy_file_template = "energy_"
    position_file_template = "position_"
    ext = ".npy"

    def __init__(self, dump_dir: str):
        if not Path(dump_dir).exists():
            raise FileNotFoundError(f"Dir does not exist: {dump_dir}")

        self.dump_dir = dump_dir
        self.buffer_size = Ray.buffer_size

        self.num_rays = 0
        self.step = 0
        self.buffer_fill = 0

        self.position = np.array([])
        self.energy = np.array([])

    def load_step(self, step: int) -> dict[str, np.ndarray] | None:
        position_filename = (MovieFromDump.position_file_template + str(step) + MovieFromDump.ext)
        position_fpath = Path(self.dump_dir) / position_filename

        energy_filename = (MovieFromDump.energy_file_template + str(step) + MovieFromDump.ext)
        energy_fpath = Path(self.dump_dir) / energy_filename

        if not position_fpath.exists() or not energy_fpath.exists():
            logger.warning(f"No state file for step {step}")
            return None

        position = np.load(position_fpath)
        energy = np.load(energy_fpath)

        if self.num_rays == 0:
            self.num_rays = energy.size
            self.position = np.zeros((self.num_rays, 3, self.buffer_size))
            self.energy = np.zeros((self.num_rays, self.buffer_size))

        if self.buffer_fill < self.buffer_size:
            self.position[:, :, self.buffer_fill] = position
            self.energy[:, self.buffer_fill] = energy
            self.buffer_fill += 1
        else:
            self.position = np.roll(self.position, shift=1, axis=2)
            self.energy = np.roll(self.energy, shift=1, axis=1)
            self.position[:, :, 0] = position
            self.energy[:, 0] = energy

        return {"position": self.position, "energy": self.energy}

    def __iter__(self):
        self.step = 0
        return self

    def __next__(self):
        self.step += 1
        self.state = self.load_step(self.step)
        if self.state is None:
            raise StopIteration
        return self.state
