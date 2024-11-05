from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.io.arrayformat import from_array_format
from building3d.io.arrayformat import to_array_format
from building3d.io.b3d import read_b3d
from building3d.io.b3d import write_b3d
from building3d.io.dotbim import read_dotbim
from building3d.io.dotbim import write_dotbim
from building3d.io.stl import read_stl
from building3d.io.stl import write_stl

if __name__ == "__main__":
    print(
        "This example creates a 3-solid building,\n"
        "saves it to various formats and recovers back,\n"
        "each time plotting the building to confirm it looks the same."
    )
    output_dir = "out/io_example"

    zone = Zone(
        [
            box(1, 1, 1, (0, 0, 0), "s1"),
            box(1, 2, 1, (1, 0, 0), "s2"),
            box(2, 1, 1, (1, 0, 1), "s3"),
        ],
        "zone",
    )

    building = Building([zone], "building")
    print("Original building")
    plot_objects((building,))

    write_b3d(f"{output_dir}/building.b3d", building, parent_dirs=True)
    building = read_b3d(f"{output_dir}/building.b3d")
    print("Saved and loaded from B3D")
    plot_objects((building,))

    write_dotbim(f"{output_dir}/building.bim", building, parent_dirs=True)
    building = read_dotbim(f"{output_dir}/building.bim")
    print("Saved and loaded from .bim")
    plot_objects((building,))

    write_stl(f"{output_dir}/building.stl", building, parent_dirs=True)
    building = read_stl(f"{output_dir}/building.stl")
    print("Saved and loaded from STL")
    plot_objects((building,))

    points, faces, polygons, walls, solids, zones = to_array_format(building)
    building = from_array_format(points, faces, polygons, walls, solids, zones)
    print("Saved and loaded from array format")
    plot_objects((building,))
