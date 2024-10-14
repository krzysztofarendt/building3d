import os
import logging

import numpy as np

from building3d.paths.wildcardpath import WildcardPath
from .config import POSITION_FILE, ENERGY_FILE, VELOCITY_FILE, HITS_FILE
from building3d.geom.types import PointType
from building3d.geom.types import VectorType
from building3d.geom.types import FloatDataType
from building3d.geom.types import IntDataType
from building3d.geom.types import FLOAT
from building3d.geom.types import INT


logger = logging.getLogger(__name__)


def dump_buffers(
    pos_buf: PointType,
    vel_buf: VectorType,
    enr_buf: FloatDataType,
    hit_buf: IntDataType,
    dump_dir: str,
):
    """Saves buffer arrays to a chosen directory.

    Each step is saved in a separate file.

    Args:
        pos_buf: buffer of ray positions, shaped (num_steps + 1, num_rays, 3)
        vel_buf: buffer of ray velocity, shaped (num_steps + 1, num_rays, 3)
        enr_buf: buffer of ray energy, shaped (num_steps + 1, num_rays)
        hit_buf: buffer of ray absorber hits, shaped (num_steps + 1, num_rays)
        dump_dir: path to the dump directory, will be created if doesn't exist

    Returns:
        None
    """
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


def read_buffers(dump_dir: str) -> tuple[PointType, VectorType, FloatDataType, IntDataType]:
    """Read buffer arrays from a directory.

    Args:
        dump_dir: path to the dump directory

    Returns:
        (pos_buf, vel_buf, enr_buf, hit_buf)
    """
    wpath_pos = WildcardPath(POSITION_FILE)
    wpath_vel = WildcardPath(VELOCITY_FILE)
    wpath_enr = WildcardPath(ENERGY_FILE)
    wpath_hit = WildcardPath(HITS_FILE)

    dict_pos = wpath_pos.get_matching_paths_dict_values(parent=dump_dir)
    dict_vel = wpath_vel.get_matching_paths_dict_values(parent=dump_dir)
    dict_enr = wpath_enr.get_matching_paths_dict_values(parent=dump_dir)
    dict_hit = wpath_hit.get_matching_paths_dict_values(parent=dump_dir)

    max_step_pos = max([d["step"] for d in dict_pos.values()])
    max_step_vel = max([d["step"] for d in dict_vel.values()])
    max_step_enr = max([d["step"] for d in dict_enr.values()])
    max_step_hit = max([d["step"] for d in dict_hit.values()])
    assert max_step_pos == max_step_vel == max_step_enr == max_step_hit, \
        "Different number of buffer steps in the dump dir?"

    max_step = max_step_pos

    # Initialize to avoid complaints from the linter about possibly unbound variables
    pos_buf = np.array([], dtype=FLOAT)
    vel_buf = np.array([], dtype=FLOAT)
    enr_buf = np.array([], dtype=FLOAT)
    hit_buf = np.array([], dtype=INT)

    for step_num in range(max_step):
        pos_path = wpath_pos.fill(parent=dump_dir, step=step_num)
        pos = np.load(pos_path)

        vel_path = wpath_vel.fill(parent=dump_dir, step=step_num)
        vel = np.load(vel_path)

        enr_path = wpath_enr.fill(parent=dump_dir, step=step_num)
        enr = np.load(enr_path)

        hit_path = wpath_hit.fill(parent=dump_dir, step=step_num)
        hit = np.load(hit_path)

        num_rays = pos.shape[0]
        num_absorbers = hit.shape[0]

        if step_num == 0:
            pos_buf = np.zeros((max_step, num_rays, 3), dtype=FLOAT)
            vel_buf = np.zeros((max_step, num_rays, 3), dtype=FLOAT)
            enr_buf = np.zeros((max_step, num_rays), dtype=FLOAT)
            hit_buf = np.zeros((max_step, num_absorbers), dtype=INT)

        pos_buf[step_num, :, :] = pos
        vel_buf[step_num, :, :] = vel
        enr_buf[step_num, :] = enr
        hit_buf[step_num, :] = hit

    return pos_buf, vel_buf, enr_buf, hit_buf
