import pytest

from building3d.geom.numba.solid.box import box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building
from building3d.geom.numba.building.graph import graph_polygon
from building3d.geom.numba.building.graph import graph_wall
from building3d.geom.numba.building.graph import graph_solid
from building3d.geom.numba.building.graph import graph_zone


@pytest.fixture
def bdg():
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
    return bdg


@pytest.fixture
def g_def(bdg):
    return graph_polygon(bdg)


@pytest.fixture
def g_fac(bdg):
    return graph_polygon(bdg, facing=True, overlapping=False, touching=False)


@pytest.fixture
def g_ove(bdg):
    return graph_polygon(bdg, facing=False, overlapping=True, touching=False)


@pytest.fixture
def g_all(bdg):
    g_all = graph_polygon(bdg, facing=True, overlapping=True, touching=True)
    return g_all


def test_graph_polygon(g_def, g_fac, g_ove, g_all):
    assert set(g_def["b/z0/s0/wall-1/wall-1"]) == set(["b/z0/s2/wall-3/wall-3"])
    assert set(g_def["b/z0/s2/wall-3/wall-3"]) == set(
        ["b/z0/s0/wall-1/wall-1", "b/z0/s1/wall-1/wall-1"]
    )
    assert set(g_def["b/z0/s0/wall-2/wall-2"]) == set(["b/z0/s1/wall-0/wall-0"])
    assert set(g_def["b/z0/s1/wall-0/wall-0"]) == set(["b/z0/s0/wall-2/wall-2"])
    assert set(g_def["b/z0/s1/wall-1/wall-1"]) == set(["b/z0/s2/wall-3/wall-3"])

    assert set(g_fac["b/z0/s0/wall-2/wall-2"]) == set(["b/z0/s1/wall-0/wall-0"])
    assert set(g_fac["b/z0/s1/wall-0/wall-0"]) == set(["b/z0/s0/wall-2/wall-2"])

    assert set(g_ove["b/z0/s0/wall-1/wall-1"]) == set(["b/z0/s2/wall-3/wall-3"])
    assert set(g_ove["b/z0/s1/wall-1/wall-1"]) == set(["b/z0/s2/wall-3/wall-3"])
    assert set(g_ove["b/z0/s2/wall-3/wall-3"]) == set(
        ["b/z0/s0/wall-1/wall-1", "b/z0/s1/wall-1/wall-1"]
    )

    assert len(g_all.keys()) > len(g_def.keys())


def test_graph_wall_solid_zone(bdg, g_def):
    gw = graph_wall(bdg, g=g_def)
    assert len(list(gw.keys())) == len(list(g_def.keys()))  # Because each wall contains 1 polygon

    gs = graph_solid(bdg, g=g_def)
    assert len(list(gs.keys())) < len(list(gw.keys()))  # Because there's less solids than walls
    assert "b/z0/s0" in gs["b/z0/s2"]
    assert "b/z0/s1" in gs["b/z0/s2"]

    gz = graph_zone(bdg, g=g_def)
    assert len(list(gz.keys())) < len(list(gs.keys()))  # Because there's less zones than solids
    assert ("b/z0" not in gz) and ("b/z1" not in gz)  # Because they are only touching
