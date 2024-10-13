import os
import logging
from pathlib import Path

import numpy as np

from building3d.paths.wildcardpath import WildcardPath
from .config import (
    ENERGY_FILE,
    POSITION_FILE,
    RAY_LINE_LEN,
)

logger = logging.getLogger(__name__)


class DumpReader:

    energy_file_template = ENERGY_FILE
    position_file_template = POSITION_FILE
    buffer_size = RAY_LINE_LEN

    def __init__(self, state_dir: str):
        if not Path(state_dir).exists():
            raise FileNotFoundError(f"Dir does not exist: {state_dir}")

        self.state_dir = state_dir

        self.num_rays = 0
        self.step = 0

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
        pos_fpath = WildcardPath(DumpReader.position_file_template).fill(
            self.state_dir, step=step
        )
        enr_fpath = WildcardPath(DumpReader.energy_file_template).fill(
            self.state_dir, step=step
        )

        if not os.path.exists(pos_fpath) or not os.path.exists(enr_fpath):
            logger.warning(f"No state file for step {step}. Return None.")
            return None

        position = np.load(pos_fpath)
        energy = np.load(enr_fpath)

        if self.num_rays == 0:
            self.num_rays = energy.size
            self.position = np.zeros((self.num_rays, 3, DumpReader.buffer_size))
            self.energy = np.ones((self.num_rays, DumpReader.buffer_size))

        self.position = np.roll(
            self.position, shift=1, axis=2
        )  # TODO: seems to be slow
        self.energy = np.roll(self.energy, shift=1, axis=1)  # TODO: seems to be slow
        self.position[:, :, 0] = position
        self.energy[:, 0] = energy

        return {"position": self.position, "energy": self.energy}

    def __iter__(self):
        self.step = 0
        return self

    def __next__(self):
        self.state = self.load_step(self.step)
        self.step += 1  # TODO: Shouldn't it be one line below?
        if self.state is None:
            raise StopIteration
        return self.state

