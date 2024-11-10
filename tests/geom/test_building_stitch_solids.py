from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.solid.box import box
from building3d.geom.solid.stitch import stitch_solids
from building3d.geom.zone import Zone


def test_building_stitch_solids(show=False):
    # Create a U-shaped building
    H = 2.0
    s0 = box(2, 8, H, (0, 0, 0), "s0")  # Adj. to s1
    s1 = box(6, 2, H, (2, 6, 0), "s1")  # Adj. to s0 and s2
    s2 = box(2, 6, H, (6, 0, 0), "s2")  # Adj. to s1

    zone = Zone([s0, s1, s2], "z")
    building = Building([zone], "b")

    if show:
        print("Before stitching...")
        plot_objects((building, ))

    # Slice adjacent polygons to make interfaces between adjacent solids
    building.stitch_solids()

    if show:
        print("After stitching...")
        plot_objects((building, ))


if __name__ == "__main__":
    test_building_stitch_solids(show=True)
