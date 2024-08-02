from pathlib import Path
from multiprocessing import Process

from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.simulators.rays.movie import make_movie
from building3d.io.b3d import write_b3d
from .simulator import simulation_job
from .merge_results import merge_results
from .config import MERGED_JOBS_DIR, STATE_DIR, B3D_FILE


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
    sim_dpath = Path(sim_dir)
    if not sim_dpath.exists():
        sim_dpath.mkdir(parents=True)

    b3d_file = str(sim_dpath / B3D_FILE)
    write_b3d(str(b3d_file), building)

    jobs = []
    for i in range(num_jobs):
        job_dir = sim_dpath / f"job_{i}"
        job_dir.mkdir(exist_ok=True, parents=False)

        p = Process(
            target=simulation_job,
            args=(
                building,  # building
                source,  # source
                sinks,  # sinks
                sink_radius,  # sink_radius
                num_rays // num_jobs,  # num_rays
                properties,  # properties
                str(job_dir / f"hits_{i}.csv"),  # csv_file
                str(job_dir / "states"),  # state_dump_dir
                steps,  # steps
                str(Path(sim_dir) / f"job_{i}.log"),  # logfile
            )
        )
        p.start()
        jobs.append(p)

    for i in range(num_jobs):
        jobs[i].join()

    # Merge results
    merge_dir = str(Path(sim_dir) / "all")
    merge_results(sim_dir=sim_dir, merge_dir=merge_dir)

    # TODO: Make movie
    movie_file = str(sim_dpath / "simulation.mp4")
    state_dump_dir = str(sim_dpath / MERGED_JOBS_DIR / STATE_DIR)
    building_file = str(sim_dpath / "building.b3d")
    make_movie(movie_file, state_dump_dir, building_file)
