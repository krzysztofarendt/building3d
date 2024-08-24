from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building
from building3d.geom.numba.building.graph import graph


def test_building_graph():
    zone = Zone(
        [
            box(1, 1, 1, (0, 0, 0), "s1"),
            box(1, 2, 1, (1, 0, 0), "s2"),
            box(2, 1, 1, (1, 0, 1), "s3"),
        ],
        "zone",
    )
    bdg = Building([zone], "building")
    graph(bdg)
    # TODO
    ...


if __name__ == "__main__":
    test_building_graph()
