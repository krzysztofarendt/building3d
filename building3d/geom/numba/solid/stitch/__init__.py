import numpy as np

from building3d.geom.numba.points import find_close_pairs
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.slice import slice_polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.exceptions import GeometryError
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths import PATH_SEP


def stitch_solids(s1: Solid, s2: Solid, adj: list | None = None) -> None:
    """Slice adjacent polygons of two solids so that they share vertices and edges.
    """
    # Find adjacent polygons
    if adj is None:
        adj = find_adjacent_polygons(s1, s2)

    # Process next pair of adjacent polygons
    if len(adj) > 0:
        p1, p2 = adj.pop()
        slice_and_replace(s1, p1, s2, p2)
        return stitch_solids(s1, s2, adj)

    else:
        return None


def slice_and_replace(s1: Solid, p1: Polygon, s2: Solid, p2: Polygon) -> None:
    """Slices polygons `p1` and `p2` and replaces them in solids `s1` and `s2`.
    """
    if p1.contains_polygon(p2) or p2.contains_polygon(p1):
        pass  # TODO: Additional slice needed
        # Proposed algorithm:
        # 1. Find two pairs of mutually visible points between p1 and p2
        # 2. Make a aux. polygon with them (though slice_polygon()?)
        # 3. Then proceed to slicing the main polygon as below

    p1a, p1b = slice_polygon(p1, p2.pts)
    assert (p1a is not None) and (p1b is not None)
    replace_polygon(s1, p1, p1a, p1b)

    p2a, p2b = slice_polygon(p2, p1.pts)
    assert (p2a is not None) and (p2b is not None)
    replace_polygon(s2, p2, p2a, p2b)

    return None


def replace_polygon(s: Solid, old_poly: Polygon, *new_poly: Polygon) -> None:
    """Replaces `old_poly` with an arbitraty number of `new_poly`. Works in-place.
    """
    wpl = get_walls_and_polygons(s)
    for wall, poly in wpl:
        if poly.name == old_poly.name:
            wall.replace_polygon(poly.name, *new_poly)


def get_walls_and_polygons(s: Solid) -> list[tuple[Wall, Polygon]]:
    """Returns a list of tuples with walls and polygons for this solid.
    """
    walls = s.get_walls()
    wpl = []
    for w in walls:
        for p in w.get_polygons():
            wpl.append((w, p))

    return wpl


def find_adjacent_polygons(s1: Solid, s2: Solid) -> list[tuple[Polygon, Polygon]]:
    """Returns a list of pairs of adjacent polygons. Those matching exactly are omitted.
    """
    adj = []
    for _, p1 in get_walls_and_polygons(s1):
        for _, p2 in get_walls_and_polygons(s2):
            facing_exactly = p1.is_facing_polygon(p2, exact=True)
            if facing_exactly:
                continue
            adjacent = p1.is_facing_polygon(p2, exact=False)
            if adjacent:
                adj.append((p1, p2))

    return adj
