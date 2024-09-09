import os

from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.points import new_point
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.io.b3d import write_b3d
from building3d.logger import init_logger
from building3d.simulators.rays.config import MAIN_LOG_FILE
from building3d.simulators.rays.movie import make_movie
from building3d.simulators.rays.simulator import RaySimulator


def example_simulation():
    project_dir = "tmp/ray_example/"
    main_logfile = os.path.join(project_dir, MAIN_LOG_FILE)
    init_logger(main_logfile)

    L = 1
    W = 1
    H = 1

    xlim = L
    ylim = W
    zlim = H
    s1 = box(xlim, ylim, zlim, name="s1")
    xlim = L
    ylim = W
    zlim = H
    s2 = box(xlim, ylim, zlim, (L, 0, 0), name="s2")
    xlim = L
    ylim = W
    zlim = H
    s3 = box(xlim, ylim, zlim, (L * 2, 0, 0), name="s3")
    z = Zone([s1, s2, s3], "z")

    building = Building([z], "b")
    b3d_file = os.path.join(project_dir, "building.b3d")
    write_b3d(b3d_file, building)

    csv_file = os.path.join(project_dir, "test_result.csv")
    if os.path.exists(csv_file):
        os.remove(csv_file)

    state_dump_dir = os.path.join(project_dir, "state_dump")

    raysim = RaySimulator(
        building=building,
        source=new_point(0.3, 0.3, 0.3),
        sinks=[new_point(0.6, 0.6, 0.6)],
        sink_radius=0.1,
        num_rays=1000,
        csv_file=csv_file,
        state_dump_dir=state_dump_dir,
    )
    plot_objects(
        (building, raysim.rays), output_file=os.path.join(project_dir, "start.png")
    )

    raysim.simulate(400)

    plot_objects(
        (building, raysim.rays), output_file=os.path.join(project_dir, "end.png")
    )

    print("Making movie")
    movie_path = os.path.join(project_dir, "simulation.mp4")
    make_movie(movie_path, state_dump_dir, b3d_file, 300)


if __name__ == "__main__":
    example_simulation()
