from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building
from building3d.io.numba.b3d import write_b3d, read_b3d
from building3d.io.numba.dotbim import write_dotbim, read_dotbim
from building3d.io.numba.stl import write_stl, read_stl


if __name__ == "__main__":
    zone = Zone(
        [
            box(1, 1, 1, (0, 0, 0), "s1"),
            box(1, 2, 1, (1, 0, 0), "s2"),
            box(2, 1, 1, (1, 0, 1), "s3"),
        ],
        "zone",
    )

    building = Building([zone], "building")

    write_b3d("temp/xxx.b3d", building, parent_dirs=True)
    building = read_b3d("temp/xxx.b3d")
    plot_objects((building,))

    write_dotbim("temp/xxx.bim", building, parent_dirs=True)
    building = read_dotbim("temp/xxx.bim")
    plot_objects((building,))

    write_stl("temp/xxx.stl", building, parent_dirs=True)
    building = read_stl("temp/xxx.stl")
    plot_objects((building,))
