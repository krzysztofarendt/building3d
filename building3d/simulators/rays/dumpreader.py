import logging
from pathlib import Path

import numpy as np

from .config import ENERGY_FILE, POSITION_FILE, DUMP_EXT, RAY_LINE_LEN


logger = logging.getLogger(__name__)


class DumpReader:

    energy_file_template = ENERGY_FILE
    position_file_template = POSITION_FILE
    ext = DUMP_EXT
    buffer_size = RAY_LINE_LEN

    def __init__(self, dump_dir: str):
        if not Path(dump_dir).exists():
            raise FileNotFoundError(f"Dir does not exist: {dump_dir}")

        self.dump_dir = dump_dir

        self.num_rays = 0
        self.step = 0
        self.buffer_fill = 0

        self.position = np.array([])
        self.energy = np.array([])

    def load_step(self, step: int) -> dict[str, np.ndarray] | None:
        """Load position and energy for step `step`

        Both position and energy and loaded into arrays having
        a cyclic buffer as the last dimension, i.e.:
        - position array shape: (num_rays, 3, buffer_size)
        - energy array shape: (num_rays, buffer_size)

        The buffers are initialized with zeros. The newest value is at `[...,0]`.
        The oldest value is at `[..., -1]`.
        """
        position_filename = (DumpReader.position_file_template + str(step) + DumpReader.ext)
        position_fpath = Path(self.dump_dir) / position_filename

        energy_filename = (DumpReader.energy_file_template + str(step) + DumpReader.ext)
        energy_fpath = Path(self.dump_dir) / energy_filename

        if not position_fpath.exists() or not energy_fpath.exists():
            logger.warning(f"No state file for step {step}. Return None.")
            return None

        position = np.load(position_fpath)
        energy = np.load(energy_fpath)

        if self.num_rays == 0:
            self.num_rays = energy.size
            self.position = np.zeros((self.num_rays, 3, DumpReader.buffer_size))
            self.energy = np.ones((self.num_rays, DumpReader.buffer_size))

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
