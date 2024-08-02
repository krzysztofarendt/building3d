from pathlib import Path
from multiprocessing import Process

from building3d.geom.building import Building
from building3d.geom.point import Point
from .simulator import simulation_job
from .merge_results import merge_results


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

    # TODO: Merge results
    merge_dir = str(Path(sim_dir) / "all")
    merge_results(sim_dir=sim_dir, merge_dir=merge_dir)

    # TODO: Make movie
    ...
