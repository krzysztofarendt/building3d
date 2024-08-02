import os
from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


JOB_DIR_PATTERN = r"^job_(?P<number>\d+$)"
RES_CSV_PATTERN = r"^hits_(?P<number>\d+)\.csv$"


def merge_results(sim_dir: str, merge_dir: str):
    """Merge job results and save to `merge_dir`."""
    # Create directory to store merged results
    merge_dpath = Path(merge_dir)
    if not merge_dpath.exists():
        merge_dpath.mkdir(parents=True)

    # Merge states
    ...  # TODO

    # Merge result CSVs
    df = merge_csv(sim_dir)
    df.to_csv(os.path.join(merge_dir, "result.csv"))
    plt.plot(df)
    plt.savefig(os.path.join(sim_dir, "hits.png"))

    # Copy job logs
    ...  # TODO

    # Delete job dirs
    ...  # TODO


def merge_csv(sim_dir: str) -> pd.DataFrame:
    df = pd.DataFrame()

    index_col = "time"
    index_num_digits = 5

    job_dirs = get_matching_paths(sim_dir, JOB_DIR_PATTERN)
    job_csvs = []
    for jd in job_dirs:
        matching = get_matching_paths(jd, RES_CSV_PATTERN)
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
    for f in os.listdir(directory):
        if p.match(f):
            paths.append(os.path.join(directory, f))
    return sorted(paths)
