from numba import njit
import numpy as np

from building3d.geom.numba.types import PointType
from building3d.geom.numba.points.find_close_pairs import find_close_pairs
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


@njit
def get_sup_cut(pairs: PointType) -> PointType:
    """Returns points to be used to slice supporting polygon."""
    pts = pairs.reshape((-1, 3))
    tmp = pts[0].copy()
    pts[0] = pts[1].copy()
    pts[1] = tmp
    return pts


def get_main_poly(pts, pairs):
    ...


def slice_and_replace(s1: Solid, p1: Polygon, s2: Solid, p2: Polygon) -> None:
    """Slices polygons `p1` and `p2` and replaces them in solids `s1` and `s2`.
    """
    p2_in_p1 = p1.contains_polygon(p2)
    p1_in_p2 = p2.contains_polygon(p1)

    if p2_in_p1 or p1_in_p2:
        # One polygon is completely inside the other
        # Algorithm:
        # - find close pairs which are mutually visible
        # - slice the large polygon into 2: main + supporting
        # - the supporting polygon needs to touch the edges of the large and small polygons
        # - then slice the main polygon using the points of the small polygon
        # Result:
        # - large polygon is sliced twice
        # - small polygon is not sliced
        # TODO: REFACTORING NEEDED
        pairs = find_close_pairs(p1.pts, p2.pts, n=2, vis_only=True)
        sup_cut = get_sup_cut(pairs)

        if p2_in_p1:
            # Slice p1 twice
            main, sup = slice_polygon(p1, sup_cut)
            assert (main is not None) and (sup is not None)
            if not np.allclose(main.vn, p1.vn):
                main = main.flip()
            if not np.allclose(sup.vn, p1.vn):
                sup = sup.flip()
            replace_polygon(s1, p1, main, sup)
            a, b = slice_polygon(main, p2.pts)
            if (a is not None) and (b is not None):
                replace_polygon(s1, main, a, b)

        elif p1_in_p2:
            # Slice p2 twice
            main, sup = slice_polygon(p2, sup_cut)
            assert (main is not None) and (sup is not None)
            if not np.allclose(main.vn, p2.vn):
                main = main.flip()
            if not np.allclose(sup.vn, p2.vn):
                sup = sup.flip()
            replace_polygon(s2, p2, main, sup)
            a, b = slice_polygon(main, p1.pts)
            if (a is not None) and (b is not None):
                replace_polygon(s2, main, a, b)
        else:
            raise RuntimeError("Should not happen")

    else:
        # The polygons are overlapping
        p1a, p1b = slice_polygon(p1, p2.pts)
        if (p1a is not None) and (p1b is not None):
            replace_polygon(s1, p1, p1a, p1b)

        p2a, p2b = slice_polygon(p2, p1.pts)
        if (p2a is not None) and (p2b is not None):
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
                assert np.allclose(p1.vn, -1 * p2.vn)
                adj.append((p1, p2))

    return adj
