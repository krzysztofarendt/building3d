from building3d.display.plot_objects import plot_objects
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.io.arrayformat import to_array_format
from building3d.io.arrayformat import from_array_format


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

    points, faces, polygons, walls, solids, zones = to_array_format(building)
    building = from_array_format(points, faces, polygons, walls, solids, zones)
    plot_objects((building,))
