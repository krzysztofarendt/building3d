from typing import Iterable

import numpy as np

from building3d.geom.paths import PATH_SEP
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building


def graph_polygon(
    bdg: Building,
    facing=True,
    overlapping=True,
    touching=False,
) -> dict[str, list[str]]:
    """Makes a building graph based on polygon connections.

    Args:
        bdg: building instance
        facing: if True will include polygons which are facing
        overlapping: if True will include polygons which are overlapping
        touching: if True will include polygons which are touching

    Retruns:
        graph dictionary
    """
    g = {}
    checked = set()

    for pl1 in iter_polygons(bdg):
        for pl2 in iter_polygons(bdg):
            if pl1 is pl2:
                continue
            if (pl1.path, pl2.path) not in checked:
                cond = []
                if facing:
                    cond.append(pl1.is_facing_polygon(pl2))
                if overlapping:
                    cond.append(pl1.is_crossing_polygon(pl2))
                if touching:
                    cond.append(pl1.is_touching_polygon(pl2))

                if np.array(cond).any():
                    if pl1.path in g:
                        g[pl1.path].append(pl2.path)
                    else:
                        g[pl1.path] = [pl2.path]
                    if pl2.path in g:
                        g[pl2.path].append(pl1.path)
                    else:
                        g[pl2.path] = [pl1.path]
                    checked.add((pl1.path, pl2.path))
                    checked.add((pl2.path, pl1.path))
    return g


def graph_wall(
    bdg: Building,
    facing=True,
    overlapping=True,
    touching=False,
    g: dict | None = None
) -> dict[str, list[str]]:
    """Makes a building graph based on wall connections.

    The output is based on the analysis of the underlaying polygons.

    Args:
        bdg: building instance
        facing: if True will include polygons which are facing
        overlapping: if True will include polygons which are overlapping
        touching: if True will include polygons which are touching

    Retruns:
        graph dictionary
    """
    if g is not None:
        g = graph_polygon(bdg, facing, overlapping, touching)
    else:
        g = {}
    return strip_graph(g, n=1)


def graph_solid(
    bdg: Building,
    facing=True,
    overlapping=True,
    touching=False,
    g: dict | None = None
) -> dict[str, list[str]]:
    """Makes a building graph based on solid connections.

    The output is based on the analysis of the underlaying polygons.

    Args:
        bdg: building instance
        facing: if True will include polygons which are facing
        overlapping: if True will include polygons which are overlapping
        touching: if True will include polygons which are touching

    Retruns:
        graph dictionary
    """
    if g is not None:
        g = graph_polygon(bdg, facing, overlapping, touching)
    else:
        g = {}
    return strip_graph(g, n=2)


def graph_zone(
    bdg: Building,
    facing=True,
    overlapping=True,
    touching=False,
    g: dict | None = None
) -> dict[str, list[str]]:
    """Makes a building graph based on solid connections.

    The output is based on the analysis of the underlaying polygons.

    Args:
        bdg: building instance
        facing: if True will include polygons which are facing
        overlapping: if True will include polygons which are overlapping
        touching: if True will include polygons which are touching

    Retruns:
        graph dictionary
    """
    if g is not None:
        g = graph_polygon(bdg, facing, overlapping, touching)
    else:
        g = {}
    return strip_graph(g, n=3)


def strip_graph(
    g: dict[str, list[str]],
    n: int,
) -> dict[str, list[str]]:
    """Removes `n` last components of all paths in the graph `g`.
    """
    gnew = {}
    for k, v in g.items():
        new_k = remove_last(k, n=n)
        new_v = list(set([remove_last(x, n=n) for x in v]))
        new_v = [x for x in new_v if x != new_k]
        if len(new_v) > 0:
            gnew[new_k] = new_v
        else:
            pass
    return gnew


def remove_last(path: str, n: int = 1) -> str:
    """Removes `n` last components of of `path`.
    """
    for _ in range(n):
        path = PATH_SEP.join(path.split(PATH_SEP)[:-1])
    return path


def iter_polygons(bdg: Building) -> Iterable[Polygon]:
    """Generator iterating over all polygons of the building.
    """
    for _, zv in bdg.children.items():
        for _, sv in zv.children.items():
            for _, wv in sv.children.items():
                for _, pv in wv.children.items():
                    yield pv


def iter_walls(bdg: Building) -> Iterable[Wall]:
    """Generator iterating over all walls of the building.
    """
    for _, zv in bdg.children.items():
        for _, sv in zv.children.items():
            for _, wv in sv.children.items():
                yield wv


def iter_solids(bdg: Building) -> Iterable[Solid]:
    """Generator iterating over all solids of the building.
    """
    for _, zv in bdg.children.items():
        for _, sv in zv.children.items():
            yield sv


def iter_zones(bdg: Building) -> Iterable[Zone]:
    """Generator iterating over all zones of the building.
    """
    for _, zv in bdg.children.items():
        yield zv
