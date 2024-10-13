import os
import logging

import numpy as np

from building3d.paths.wildcardpath import WildcardPath
from .config import POSITION_FILE, ENERGY_FILE, VELOCITY_FILE, HITS_FILE

logger = logging.getLogger(__name__)


def dump_buffers(pos_buf, vel_buf, enr_buf, hit_buf, dump_dir):
    logger.debug(f"Saving buffers to {dump_dir}")

    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)

    step = 0
    num_steps = pos_buf.shape[0] - 1

    while step <= num_steps:
        for data, file in (
            (pos_buf, POSITION_FILE),
            (enr_buf, ENERGY_FILE),
            (vel_buf, VELOCITY_FILE),
            (hit_buf, HITS_FILE),
        ):
            path = WildcardPath(file).fill(parent=dump_dir, step=step)
            np.save(path, data[step])

        step += 1
