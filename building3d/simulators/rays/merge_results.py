import os
from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


JOB_DIR_PATTERN = r".*job_(?P<number>\d+$)"
HIT_CSV_PATTERN = r".*hits_(?P<number>\d+)\.csv$"
ENR_NPY_PATTERN = r".*states/energy_(?P<number>\d+)\.npy$"
POS_NPY_PATTERN = r".*states/position_(?P<number>\d+)\.npy$"


def merge_results(sim_dir: str, merge_dir: str):
    """Merge job results and save to `merge_dir`."""
    # Create directory to store merged results
    merge_dpath = Path(merge_dir)
    if not merge_dpath.exists():
        merge_dpath.mkdir(parents=True)

    # Merge states
    merge_state(sim_dir)

    # Merge hits csv files
    df = merge_hits(sim_dir)
    df.to_csv(os.path.join(merge_dir, "hits.csv"))
    plt.plot(df)
    plt.savefig(os.path.join(sim_dir, "hits.png"))

    # Delete job dirs
    ...  # TODO


def get_step_num(path: str, pattern: str) -> int | None:
    step = None
    p = re.match(pattern, path)
    if p is not None:
        step = int(p.group("number"))

    return step


def merge_state(sim_dir: str):
    print("Merging state")

    state_dir = os.path.join(sim_dir, "all", "state")
    if not os.path.exists(state_dir):
        os.mkdir(state_dir)

    job_dirs = get_matching_paths(sim_dir, JOB_DIR_PATTERN)
    energy_files = []
    position_files = []
    num_steps = 0

    for jd in job_dirs:
        energy_files.extend(get_matching_paths(jd, ENR_NPY_PATTERN))
        position_files.extend(get_matching_paths(jd, POS_NPY_PATTERN))

    for ef in energy_files:
        step = get_step_num(ef, ENR_NPY_PATTERN)
        assert step is not None
        if step > num_steps:
            num_steps = step

    # TODO: Avoid duplicated code and cardcoded paths
    for step in range(num_steps):
        print(f"\r{step + 1}/{num_steps}", end="")
        energy = None
        position = None
        for jd in sorted(job_dirs):
            # Read state from each job dir
            arr = np.load(os.path.join(jd, "states", f"energy_{step}.npy"))
            if energy is None:
                energy = arr
            else:
                energy = np.concatenate([energy, arr])
            arr = np.load(os.path.join(jd, "states", f"position_{step}.npy"))
            if position is None:
                position = arr
            else:
                position = np.concatenate([position, arr])

        assert energy is not None
        np.save(os.path.join(state_dir, f"energy_{step}.npy"), energy)
        assert position is not None
        np.save(os.path.join(state_dir, f"position_{step}.npy"), position)

    print()


def merge_hits(sim_dir: str) -> pd.DataFrame:
    """Sum hits for each sink for each job and return a dataframe."""
    df = pd.DataFrame()

    index_col = "time"
    index_num_digits = 5

    job_dirs = get_matching_paths(sim_dir, JOB_DIR_PATTERN)
    job_csvs = []
    for jd in job_dirs:
        matching = get_matching_paths(jd, HIT_CSV_PATTERN)
        assert len(matching) == 1
        job_csvs.extend(matching)

    for csv in job_csvs:
        job_df = pd.read_csv(csv).set_index(index_col)
        job_df.index = job_df.index.round(index_num_digits)

        if df.size == 0:
            df = job_df
        else:
            for col in df.columns:
                df[col] += job_df[col]

    return df


def get_matching_paths(directory: str, pattern: str) -> list[str]:
    """Return a list of matching paths from the directory contents using a regex pattern."""
    paths = []
    p = re.compile(pattern)
    for f in Path(directory).glob("**/*"):
        f = str(f)
        if p.match(f):
            paths.append(f)
    return sorted(paths)
