import time

import pytest

from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.geom.building.graph import graph_polygon
from building3d.geom.building.graph import graph_wall
from building3d.geom.building.graph import graph_solid
from building3d.geom.building.graph import graph_zone


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
def gz_all(bdg):
    return graph_zone(bdg, facing=True, overlapping=True, touching=True)


def test_graph_polygon(g_def, g_fac, g_ove, gz_all):
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

    assert gz_all["b/z1"] == ["b/z0"]
    assert gz_all["b/z0"] == ["b/z1"]


def test_graph_wall_solid_zone(bdg, g_def):
    gw = graph_wall(bdg, g=g_def)
    assert len(list(gw.keys())) == len(
        list(g_def.keys())
    )  # Because each wall contains 1 polygon

    gs = graph_solid(bdg, g=g_def)
    assert len(list(gs.keys())) < len(
        list(gw.keys())
    )  # Because there's less solids than walls
    assert "b/z0/s0" in gs["b/z0/s2"]
    assert "b/z0/s1" in gs["b/z0/s2"]

    gz = graph_zone(bdg, g=g_def)
    assert len(list(gz.keys())) < len(
        list(gs.keys())
    )  # Because there's less zones than solids
    assert (gz["b/z0"] == []) and (gz["b/z1"] == [])  # Because they are only touching


def timed(f, *args, **kwargs):
    t0 = time.time()
    r = f(*args, **kwargs)
    t = time.time() - t0
    return t, r


def test_graph_method_caching(bdg):
    # Make sure it takes less time to get cached graphs (any after the first one)
    time_z, gz = timed(bdg.get_graph, new=False, level="zone")
    time_s, gs = timed(bdg.get_graph, new=False, level="solid")
    time_w, gw = timed(bdg.get_graph, new=False, level="wall")
    time_p, gp = timed(bdg.get_graph, new=False, level="polygon")

    assert time_z > time_s
    assert time_z > time_w
    assert time_z > time_p

    assert "b/z0" in gz
    assert "b/z0/s0" in gs
    assert "b/z0/s0/wall-0" in gw
    assert "b/z0/s0/wall-0/wall-0" in gp
