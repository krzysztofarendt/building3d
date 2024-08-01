from pathlib import Path
from multiprocessing import Process

from building3d.geom.building import Building
from building3d.geom.point import Point
from .simulator import simulation_job


def parallel_simulation(
    building: Building,
    source: Point,
    receiver: Point,
    receiver_radius: float,
    num_rays: int,
    properties: None | dict,
    out_dir: str,
    steps: int,
    num_jobs: int,
):
    out_dpath = Path(out_dir)
    if not out_dpath.exists():
        out_dpath.mkdir(parents=True)

    jobs = []
    for i in range(num_jobs):
        job_dir = out_dpath / f"job_{i}"
        job_dir.mkdir(exist_ok=True, parents=False)

        p = Process(
            target=simulation_job,
            args=(
                building,  # building
                source,  # source
                receiver,  # receiver
                receiver_radius,  # receiver_radius
                num_rays // num_jobs,  # num_rays
                properties,  # properties
                str(job_dir / f"result_{i}.csv"),  # csv_file
                str(job_dir / "states"),  # state_dump_dir
                steps,  # steps
                str(job_dir / f"job_{i}.log"),  # logfile
            )
        )
        p.start()
        jobs.append(p)

    for i in range(num_jobs):
        jobs[i].join()

    # TODO: Merge results
    ...

    # TODO: Make movie
    ...
