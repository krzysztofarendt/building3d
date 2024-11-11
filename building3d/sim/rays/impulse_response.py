import numpy as np
import pandas as pd

from building3d.geom.types import FloatDataType
from building3d.sim.rays.simulation_config import SimulationConfig


def impulse_response(hit_buf: FloatDataType, sim_cfg: SimulationConfig) -> pd.DataFrame:
    """Converts a time-aggregated hit buffer into an impulse response DataFrame.

    Takes a buffer containing cumulative ray hits over time and converts it into an
    instantaneous impulse response by computing the time derivative. The result is
    normalized to a maximum value of 1 while preserving relative differences between
    absorbers.

    Args:
        hit_buf: Array of shape (num_timesteps, num_absorbers) containing the
            cumulative number of ray hits for each absorber over time.
        sim_cfg: Simulation configuration object containing time step information.

    Returns:
        DataFrame with time index and one column per absorber containing the
        normalized impulse response values.
    """
    hit_agr = hit_buf.copy()

    num_steps = hit_agr.shape[0]
    num_absorbers = hit_agr.shape[1]
    time_step = sim_cfg.engine["time_step"]

    # Hit buffer contains data aggregated over time, so I need to take a diff
    hit_inst = np.zeros((num_steps, num_absorbers), dtype=hit_agr.dtype)
    hit_inst[0, :] = hit_agr[0, :]
    hit_inst[1:, :] = np.diff(hit_agr, n=1, axis=0)

    # Normalize so that the sum of energy = 1
    # Keep the relative differences between absorbers to account for different volumes.
    hit_inst /= hit_inst.sum(axis=0).max()

    # Make time array
    time_arr = np.arange(0, num_steps * time_step, time_step)

    # Convert to DataFrame (index: time, columns: receivers)
    ir = pd.DataFrame(index=pd.Index(time_arr, name="time"))
    for an in range(num_absorbers):
        ir[an] = hit_inst[:, an]

    return ir
