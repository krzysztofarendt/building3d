import logging
import os

import numpy as np

from building3d.geom.types import FLOAT
from building3d.geom.types import FloatDataType
from building3d.geom.types import PointType
from building3d.paths.wildcardpath import WildcardPath

from .simulation_config import SimulationConfig

logger = logging.getLogger(__name__)


def dump_buffers(
    pos_buf: PointType,
    enr_buf: FloatDataType,
    hit_buf: FloatDataType,
    dump_dir: str,
    sim_cfg: SimulationConfig,
):
    """Saves buffer arrays to a chosen directory.

    Each step is saved in a separate file.

    Args:
        pos_buf: buffer of ray positions, shaped (num_steps, num_rays, 3)
        enr_buf: buffer of ray energy, shaped (num_steps, num_rays)
        hit_buf: buffer of ray absorber hits, shaped (num_steps, num_absorbers)
        dump_dir: path to the dump directory, will be created if doesn't exist
        sim_cfg: simulation configuration

    Returns:
        None
    """
    logger.debug(f"Saving buffers to {dump_dir}")

    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)

    step = 0
    num_steps = pos_buf.shape[0]

    while step < num_steps:
        for data, file in (
            (pos_buf, sim_cfg.paths["position_file"]),
            (enr_buf, sim_cfg.paths["energy_file"]),
            (hit_buf, sim_cfg.paths["hits_file"]),
        ):
            path = WildcardPath(file).fill(parent=dump_dir, step=step)
            np.save(path, data[step])

        step += 1


def read_buffers(
    dump_dir: str,
    sim_cfg: SimulationConfig,
) -> tuple[PointType, FloatDataType, FloatDataType]:
    """Read buffer arrays from a directory.

    Args:
        dump_dir: path to the dump directory
        sim_cfg: simulation configuration

    Returns:
        (pos_buf, enr_buf, hit_buf)
    """
    wpath_pos = WildcardPath(sim_cfg.paths["position_file"])
    wpath_enr = WildcardPath(sim_cfg.paths["energy_file"])
    wpath_hit = WildcardPath(sim_cfg.paths["hits_file"])

    dict_pos = wpath_pos.get_matching_paths_dict_values(parent=dump_dir)
    dict_enr = wpath_enr.get_matching_paths_dict_values(parent=dump_dir)
    dict_hit = wpath_hit.get_matching_paths_dict_values(parent=dump_dir)

    max_step_pos = max([d["step"] for d in dict_pos.values()]) + 1  # Because indexing starts at 0
    max_step_enr = max([d["step"] for d in dict_enr.values()]) + 1
    max_step_hit = max([d["step"] for d in dict_hit.values()]) + 1
    assert (
        max_step_pos == max_step_enr == max_step_hit
    ), "Different number of buffer steps in the dump dir?"

    max_step = max_step_pos

    # Initialize to avoid complaints from the linter about possibly unbound variables
    pos_buf = np.array([], dtype=FLOAT)
    enr_buf = np.array([], dtype=FLOAT)
    hit_buf = np.array([], dtype=FLOAT)

    for step_num in range(max_step):
        pos_path = wpath_pos.fill(parent=dump_dir, step=step_num)
        pos = np.load(pos_path)

        enr_path = wpath_enr.fill(parent=dump_dir, step=step_num)
        enr = np.load(enr_path)

        hit_path = wpath_hit.fill(parent=dump_dir, step=step_num)
        hit = np.load(hit_path)

        num_rays = pos.shape[0]
        num_absorbers = hit.shape[0]

        if step_num == 0:
            pos_buf = np.zeros((max_step, num_rays, 3), dtype=FLOAT)
            enr_buf = np.zeros((max_step, num_rays), dtype=FLOAT)
            hit_buf = np.zeros((max_step, num_absorbers), dtype=FLOAT)

        pos_buf[step_num, 0:num_rays, 0:3] = pos
        enr_buf[step_num, 0:num_rays] = enr
        hit_buf[step_num, 0:num_absorbers] = hit

    return pos_buf, enr_buf, hit_buf
