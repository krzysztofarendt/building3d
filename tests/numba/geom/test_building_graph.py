from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building
from building3d.geom.numba.building.graph import graph_polygon


def test_building_graph():
    z0 = Zone(
        [
            box(1, 1, 1, (0, 0, 0), "s0"),  # facing s1, touching s3
            box(1, 1, 1, (0, 1, 0), "s1"),  # facing s0
            box(1, 1, 1, (1, 0.5, 0), "s2"),  # overlapping s0, s1
        ],
        "z0",
    )
    z1 = Zone(
        [
            box(1, 1, 1, (-1, -1, 0), "s3"),  # touching s0
        ],
        "z1",
    )
    bdg = Building([z0, z1], "b")
    g_def = graph_polygon(bdg)
    g_fac = graph_polygon(bdg, facing=True, overlapping=False, touching=False)
    g_ove = graph_polygon(bdg, facing=False, overlapping=True, touching=False)

    assert set(g_def["b/z0/s0/wall-1/wall-1"]) == set(["b/z0/s2/wall-3/wall-3"])
    assert set(g_def["b/z0/s2/wall-3/wall-3"]) == set(["b/z0/s0/wall-1/wall-1",
                                                       "b/z0/s1/wall-1/wall-1"])
    assert set(g_def["b/z0/s0/wall-2/wall-2"]) == set(["b/z0/s1/wall-0/wall-0"])
    assert set(g_def["b/z0/s1/wall-0/wall-0"]) == set(["b/z0/s0/wall-2/wall-2"])
    assert set(g_def["b/z0/s1/wall-1/wall-1"]) == set(["b/z0/s2/wall-3/wall-3"])

    assert set(g_fac["b/z0/s0/wall-2/wall-2"]) == set(["b/z0/s1/wall-0/wall-0"])
    assert set(g_fac["b/z0/s1/wall-0/wall-0"]) == set(["b/z0/s0/wall-2/wall-2"])

    assert set(g_ove["b/z0/s0/wall-1/wall-1"]) == set(["b/z0/s2/wall-3/wall-3"])
    assert set(g_ove["b/z0/s1/wall-1/wall-1"]) == set(['b/z0/s2/wall-3/wall-3'])
    assert set(g_ove["b/z0/s2/wall-3/wall-3"]) == set(["b/z0/s0/wall-1/wall-1",
                                                       "b/z0/s1/wall-1/wall-1"])

    # TODO: This takes a lot of time
    # g_all = graph_polygon(bdg, facing=True, overlapping=True, touching=True)
    # assert len(g_all.keys()) > len(g_def.keys())


if __name__ == "__main__":
    test_building_graph()
