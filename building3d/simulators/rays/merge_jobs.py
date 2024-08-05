import numpy as np
import pandas as pd

from building3d.paths.wildcardpath import WildcardPath


def merge_state(
    sim_dir: str,
    mrg_enr_template: str,
    mrg_pos_template: str,
    job_enr_template: str,
    job_pos_template: str,
):
    print("Merging state")

    # Get state file mapping: {(<job>, <step>): path}
    job_enr_wp = WildcardPath(job_enr_template)
    job_pos_wp = WildcardPath(job_pos_template)
    job_enr_map = job_enr_wp.get_matching_paths_namedtuple_keys(parent=sim_dir)
    job_pos_map = job_pos_wp.get_matching_paths_namedtuple_keys(parent=sim_dir)

    # Find:
    # - max. <job>
    # - max. <step>
    max_job_num = 0
    max_step_num = 0
    for w in job_pos_map.keys():
        if w.job > max_job_num:
            max_job_num = w.job
        if w.step > max_step_num:
            max_step_num = w.step

    max_job_num += 1  # must increase, becasue if jobs==N, max. job number in job_<job> is N-1
    max_step_num += 1  # like above

    mrg_enr_wp = WildcardPath(mrg_enr_template)
    mrg_pos_wp = WildcardPath(mrg_pos_template)

    for step in range(max_step_num):
        print(f"\r{step + 1}/{max_step_num}", end="")
        # Load from all jobs
        energy = None
        position = None
        for job in range(max_job_num):
            enr = np.load(job_enr_map[job_enr_wp.Case(job=job, step=step)])
            pos = np.load(job_pos_map[job_pos_wp.Case(job=job, step=step)])

            # Concatenate
            if energy is None:
                energy = enr
            else:
                energy = np.concatenate([energy, enr])

            if position is None:
                position = pos
            else:
                position = np.concatenate([position, pos])

        # Save
        assert energy is not None
        np.save(mrg_enr_wp.fill(sim_dir, step=step), energy)

        assert position is not None
        np.save(mrg_pos_wp.fill(sim_dir, step=step), position)
    print()


def merge_hits(
    sim_dir: str,
    mrg_hit_path: str,
    job_hit_template: str,
) -> None:
    """Sum hits for each sink for each job and return a dataframe."""
    hits = pd.DataFrame()
    index_col = "time"
    index_num_digits = 5

    job_hit_wp = WildcardPath(job_hit_template)
    job_hit_map = job_hit_wp.get_matching_paths_namedtuple_keys(sim_dir)

    max_job_num = 0
    for w in job_hit_map.keys():
        if w.job > max_job_num:
            max_job_num = w.job
    max_job_num += 1  # must increase, becasue if jobs==N, max. job number in job_<job> is N-1

    job_hits = []
    for job in range(max_job_num):
        job_hits.append(pd.read_csv(job_hit_map[job_hit_wp.Case(job=job)]))

    for df in job_hits:
        df = df.set_index(index_col)
        df.index = df.index.round(index_num_digits)

        if hits.size == 0:
            hits = df
        else:
            for col in df.columns:
                hits[col] += df[col]

    csv_path = WildcardPath(mrg_hit_path).fill(parent=sim_dir)
    hits.to_csv(csv_path)
