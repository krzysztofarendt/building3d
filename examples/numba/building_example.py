from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building


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

    plot_objects((building,))
