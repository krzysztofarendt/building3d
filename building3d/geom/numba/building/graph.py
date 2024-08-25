from typing import Iterable

import numpy as np

from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building


def iter_polygons(bdg: Building) -> Iterable[Polygon]:
    for _, zv in bdg.children.items():
        for _, sv in zv.children.items():
            for _, wv in sv.children.items():
                for _, pv in wv.children.items():
                    yield pv


def iter_walls(bdg: Building) -> Iterable[Wall]:
    for _, zv in bdg.children.items():
        for _, sv in zv.children.items():
            for _, wv in sv.children.items():
                yield wv


def iter_solids(bdg: Building) -> Iterable[Solid]:
    for _, zv in bdg.children.items():
        for _, sv in zv.children.items():
            yield sv


def iter_zones(bdg: Building) -> Iterable[Zone]:
    for _, zv in bdg.children.items():
        yield zv


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


def graph_wall(bdg: Building) -> dict[str, list[str]]:
    ...


def graph_solid(bdg: Building) -> dict[str, list[str]]:
    ...


def graph_zone(bdg: Building) -> dict[str, list[str]]:
    ...
