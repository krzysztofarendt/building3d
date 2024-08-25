import os
from multiprocessing import Process

from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.simulators.rays.movie import make_movie
from building3d.io.b3d import write_b3d
from building3d.paths.wildcardpath import WildcardPath
from .simulator import simulation_job
from .merge_jobs import merge_state, merge_hits
from .config import (
    MERGE_DIR,
    MERGE_HIT_CSV,
    MERGE_STATE_DIR,
    MOVIE_FILE,
    MAIN_LOG_FILE,
    B3D_FILE,
    JOB_DIR,
    JOB_STATE_DIR,
    JOB_HIT_CSV,
    JOB_LOG_FILE,
    MERGE_ENR_STATE_FILE,
    MERGE_POS_STATE_FILE,
    JOB_ENR_STATE_FILE,
    JOB_POS_STATE_FILE,
)


def parallel_simulation(
    building: Building,
    source: Point,
    sinks: list[Point],
    sink_radius: float,
    num_rays: int,
    properties: None | dict,
    sim_dir: str,
    steps: int,
    num_jobs: int,
):
    if not os.path.exists(sim_dir):
        os.makedirs(sim_dir)

    write_b3d(B3D_FILE, building)

    jobs = []
    for i in range(num_jobs):
        _ = WildcardPath(JOB_DIR).mkdir(parent=sim_dir, job=i)

        job_hit_csv = WildcardPath(JOB_HIT_CSV).fill(parent=sim_dir, job=i)
        job_state_dir = WildcardPath(JOB_STATE_DIR).fill(parent=sim_dir, job=i)
        job_log_file = WildcardPath(JOB_LOG_FILE).fill(parent=sim_dir, job=i)

        p = Process(
            target=simulation_job,
            args=(
                building,  # building
                source,  # source
                sinks,  # sinks
                sink_radius,  # sink_radius
                num_rays // num_jobs,  # num_rays
                properties,  # properties
                job_hit_csv,  # csv_file
                job_state_dir,  # state_dump_dir
                steps,  # steps
                job_log_file,  # logfile
            ),
        )
        p.start()
        jobs.append(p)

    for i in range(num_jobs):
        jobs[i].join()

    # Merge results
    merge_dir = WildcardPath(MERGE_DIR).mkdir(parent=sim_dir)
    merge_state_dir = WildcardPath(MERGE_STATE_DIR).mkdir(parent=sim_dir)
    merge_state(
        sim_dir=sim_dir,
        mrg_enr_template=MERGE_ENR_STATE_FILE,
        mrg_pos_template=MERGE_POS_STATE_FILE,
        job_enr_template=JOB_ENR_STATE_FILE,
        job_pos_template=JOB_POS_STATE_FILE,
    )
    merge_hits(
        sim_dir=sim_dir,
        mrg_hit_path=MERGE_HIT_CSV,
        job_hit_template=JOB_HIT_CSV,
    )

    # Make movie
    movie_file = WildcardPath(MOVIE_FILE).fill(parent=sim_dir)
    merge_state_dir = WildcardPath(MERGE_STATE_DIR).fill(parent=sim_dir)
    b3d_file = WildcardPath(B3D_FILE).fill(parent=sim_dir)
    make_movie(
        output_file=movie_file,
        state_dump_dir=merge_state_dir,
        building_file=b3d_file,
    )
