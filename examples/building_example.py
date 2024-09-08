from building3d.display.plot_objects import plot_objects
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.io.b3d import write_b3d, read_b3d
from building3d.io.dotbim import write_dotbim, read_dotbim
from building3d.io.stl import write_stl, read_stl


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

    write_b3d("tmp/building.b3d", building, parent_dirs=True)
    building = read_b3d("tmp/building.b3d")
    plot_objects((building,))

    write_dotbim("tmp/building.bim", building, parent_dirs=True)
    building = read_dotbim("tmp/building.bim")
    plot_objects((building,))

    write_stl("tmp/building.stl", building, parent_dirs=True)
    building = read_stl("tmp/building.stl")
    plot_objects((building,))
