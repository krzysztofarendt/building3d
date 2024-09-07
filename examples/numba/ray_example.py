import os

from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.building import Building
from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.points import new_point
from building3d.simulators.rays.numba.simulator import RaySimulator
# from building3d.simulators.rays.numba.movie import make_movie


def example_simulation():
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

    csv_file = "tmp/test_result.csv"
    if os.path.exists(csv_file):
        os.remove(csv_file)

    state_dump_dir = "tmp/state_dump/"

    raysim = RaySimulator(
        building=building,
        source=new_point(0.3, 0.3, 0.3),
        sinks=[new_point(0.6, 0.6, 0.6)],
        sink_radius=0.1,
        num_rays=1000,
        csv_file=csv_file,
        state_dump_dir=state_dump_dir,
    )
    plot_objects((building, raysim.rays), output_file="tmp/start.png")

    raysim.simulate(2000)

    plot_objects((building, raysim.rays), output_file="tmp/end.png")

    # print("Making movie")
    # movie_path = "tmp/test_ray_simulator.mp4"
    # make_movie(movie_path, state_dump_dir, b3d_file, 300)


if __name__ == "__main__":
    example_simulation()
