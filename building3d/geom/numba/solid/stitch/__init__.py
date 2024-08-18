import numpy as np

from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.slice import slice_polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.exceptions import GeometryError
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths import PATH_SEP


def stitch_solids(s1: Solid, s2: Solid, adj: list | None = None) -> None:
    """Slice adjacent polygons of two solids so that they share vertices and edges."""

    # Find adjacent polygons
    if adj is None:
        adj = find_adjacent_polygons(s1, s2)

    # Process next pair of adjacent polygons
    if len(adj) > 0:
        p1, p2 = adj.pop()
        s1, s2 = slice_and_replace(s1, p1, s2, p2)
        return stitch_solids(s1, s2, adj)

    else:
        return None


def get_polygons(s: Solid) -> list[Polygon]:
    """Returns a list of polygons belonging to solid `s`."""
    walls = s.get_walls()
    polys = []
    for w in walls:
        polys.extend(w.get_polygons())
    return polys


def get_walls_and_polygons(s: Solid) -> list[tuple[Wall, Polygon]]:
    """Returns a list of tuples with walls and polygons for this solid."""
    walls = s.get_walls()
    wpl = []
    for w in walls:
        for p in w.get_polygons():
            wpl.append((w, p))
    return wpl


def find_adjacent_polygons(s1: Solid, s2: Solid) -> list[tuple[Polygon, Polygon]]:
    """Returns a list of pairs of adjacent polygons. Those matching exactly are ommited."""

    adj = []
    for p1 in get_polygons(s1):
        for p2 in get_polygons(s2):
            facing_exactly = p1.is_facing_polygon(p2, exact=True)
            if facing_exactly:
                continue
            adjacent = p1.is_facing_polygon(p2, exact=False)
            if adjacent:
                adj.append((p1, p2))
    return adj


def replace_polygon(s: Solid, old_poly: Polygon, *new_poly: Polygon) -> None:
    """Replaces `old_poly` with an arbitraty number of `new_poly`. Works in-place."""
    wpl = get_walls_and_polygons(s)
    for wall, poly in wpl:
        if poly.name == old_poly.name:
            wall.replace_polygon(poly.name, *new_poly)


def slice_and_replace(s1: Solid, p1: Polygon, s2: Solid, p2: Polygon) -> tuple[Solid, Solid]:
    """Slices polygons `p1` and `p2` and replaces them in solids `s1` and `s2`."""
    p1a, p1b = slice_polygon(p1, p2.pts)
    if p1a and p1b:
        replace_polygon(s1, p1, p1a, p1b)
    else:
        print(f"Polygons {p1}, {p2} of {s1}, {s2} either fully enclosed or touching at one edge")
        if p1.contains_polygon(p2) or p2.contains_polygon(p1):
            print("TODO: deal with fully enclosed polygons")
            # breakpoint()  # TODO: deal with fully enclosed polygons

    p2a, p2b = slice_polygon(p2, p1.pts)
    if p2a and p2b:
        replace_polygon(s2, p2, p2a, p2b)
    else:
        print(f"Polygons {p1}, {p2} of {s1}, {s2} either fully enclosed or touching at one edge")
        if p1.contains_polygon(p2) or p2.contains_polygon(p1):
            print("TODO: deal with fully enclosed polygons")
            # breakpoint()  # TODO: deal with fully enclosed polygons

    return (s1, s2)
