from numba import njit
import numpy as np

from building3d.geom.exceptions import GeometryError
from building3d.geom.numba.types import PointType
from building3d.geom.numba.points.find_close_pairs import find_close_pairs
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.slice import slice_polygon
from building3d.geom.numba.polygon.slice.add_intersection_points import add_intersection_points
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.types import FLOAT


def stitch_solids(s1: Solid, s2: Solid) -> None:
    """Slice adjacent polygons of two solids so that they share vertices and edges.
    """
    # Find next tuple of adjacent polygons
    adj = next_adjacent_polygons(s1, s2)

    if adj is not None:
        # Process next pair of adjacent polygons
        p1, p2 = adj
        slice_both_and_replace(s1, p1, s2, p2)
        return stitch_solids(s1, s2)

    else:
        return None


def next_adjacent_polygons(s1: Solid, s2: Solid) -> tuple[Polygon, Polygon] | None:
    """Returns a pair of adjacent polygons. Those matching exactly are omitted.
    """
    for _, p1 in get_walls_and_polygons(s1):
        for _, p2 in get_walls_and_polygons(s2):
            facing_exactly = p1.is_facing_polygon(p2, exact=True)
            if facing_exactly:
                # Nothing to slice
                continue
            touching = p1.is_touching_polygon(p2)
            if touching:
                # Nothing to slice
                continue
            adjacent = p1.is_facing_polygon(p2, exact=False)
            if adjacent:
                # These can be sliced
                return p1, p2
    # There are no adjacent polygons anymore
    return None


def slice_both_and_replace(s1: Solid, p1: Polygon, s2: Solid, p2: Polygon) -> None:
    """Slices polygons `p1` and `p2` and replaces them in solids `s1` and `s2` (in-place).
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
        pairs = find_close_pairs(p1.pts, p2.pts, n=2, vis_only=True)
        sup_cut = get_sup_cut(pairs)

        if p2_in_p1:
            # Slice p1 twice
            main, sup = slice_one_and_replace(s1, p1, sup_cut)
            assert main is not None
            _, _ = slice_one_and_replace(s1, main, p2.pts)

        elif p1_in_p2:
            # Slice p2 twice
            main, sup = slice_one_and_replace(s2, p2, sup_cut)
            assert main is not None
            _, _ = slice_one_and_replace(s2, main, p1.pts)

        else:
            raise RuntimeError("Should not happen")

    else:
        # The polygons are overlapping
        _, _ = slice_one_and_replace(s1, p1, p2.pts)
        _, _ = slice_one_and_replace(s2, p2, p1.pts)

    return None


@njit
def get_sup_cut(pairs: PointType) -> PointType:
    """Returns points to be used to slice supporting polygon."""
    pts = pairs.reshape((-1, 3))
    tmp = pts[0].copy()
    pts[0] = pts[1].copy()
    pts[1] = tmp
    return pts


def slice_one_and_replace(
    s: Solid,
    p: Polygon,
    slicing_pts: PointType
) -> tuple[Polygon | None, Polygon | None]:
    """Slices polygon `p` with `slicing_pts` and replaces it in solid `s` (in-place).

    Args:
        s: Solid containing the polygon `p`
        p: Polygon from solid `s`
        slicing_pts: Slicing points

    Return:
        tuple of polygons `(a, b)`, where `b` is the polygon surrounded by `slicing_pts`
    """
    _, slicing_pts = add_intersection_points(p.pts, slicing_pts)
    slicing_pts = remove_outside_points(p, slicing_pts)

    if len(slicing_pts) < 2:
        return None, None

    pt_in_b = None  # TODO
    try:
        a, b = slice_polygon(
            p, slicing_pts, pt2=pt_in_b, name1=f"{p.name}-main", name2=f"{p.name}-sup"
        )
    except GeometryError:
        return None, None

    if not np.allclose(a.vn, p.vn):
        a = a.flip()
    if not np.allclose(b.vn, p.vn):
        b = b.flip()

    replace_polygon(s, p, a, b)

    return a, b


def replace_polygon(s: Solid, old_poly: Polygon, *new_poly: Polygon) -> None:
    """Replaces `old_poly` with an arbitraty number of `new_poly` (in-place).
    """
    wpl = get_walls_and_polygons(s)
    for wall, poly in wpl:
        if poly.name == old_poly.name:
            wall.replace_polygon(poly.name, *new_poly)


def get_walls_and_polygons(s: Solid) -> list[tuple[Wall, Polygon]]:
    """Returns a list of tuples with walls and polygons for this solid.
    """
    walls = s.children.values()
    wpl = []
    for w in walls:
        for p in w.children.values():
            wpl.append((w, p))

    return wpl


def remove_outside_points(poly: Polygon, slicing_pts: PointType) -> PointType:
    """Returns only those slicing points which are inside `poly` (boundary included).
    """
    pts = np.zeros(slicing_pts.shape, dtype=FLOAT)
    j = 0
    for i in range(slicing_pts.shape[0]):
        pt = slicing_pts[i]
        if poly.is_point_inside(pt, boundary_in=True):
            pts[j] = pt
            j += 1
    return pts[:j]

