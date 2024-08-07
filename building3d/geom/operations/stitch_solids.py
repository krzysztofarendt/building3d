import numpy as np

from building3d.util.roll_back import roll_back
from building3d.geom.line import line_segment_intersection
from building3d.geom.vector import length
from building3d.geom.vector import vector
from building3d.geom.paths import PATH_SEP
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.exceptions import GeometryError


def stitch_solids(
    sld1: Solid,
    sld2: Solid,
) -> tuple[Solid, Solid]:
    """Slice adjacent polygons of two solids so that they share vertices and edges."""

    # Check if the solids are adjacent
    if not sld1.is_adjacent_to_solid(sld2, exact=False):
        raise GeometryError(
            f"Cannot stitch solids {sld1.name} and {sld2.name}, because they are not adjacent"
        )

    # Find adjacent polygons
    adjacent = []
    for poly1 in sld1.get_polygons():
        for poly2 in sld2.get_polygons():
            if poly1.is_facing_polygon(poly2, exact=False):
                adjacent = [poly1, poly2]
                break
        if len(adjacent) == 2:
            break

    # Find out which one to slice
    # Possible cases:
    # 1) They are matching exactly (all points are equal) -> no slice needed
    # 2) poly1 is bigger, the poly2 polygon is fully within poly1 -> slice poly1
    #   a) some vertices and/or edges touching
    #   b) poly2 is not touching and vertex/edge of poly1
    # 3) poly2 is bigger, the poly1 polygon is fully within poly2 -> slice poly2
    #   a) some vertices and/or edges touching
    #   b) poly1 is not touching and vertex/edge of poly2
    # 4) They are partially overlapping -> slice both
    poly1 = adjacent[0]
    poly2 = adjacent[1]
    poly1_points_in_poly2 = np.array([poly2.is_point_inside(p) for p in poly1.points])
    poly2_points_in_poly1 = np.array([poly1.is_point_inside(p) for p in poly2.points])

    case = 0
    if poly1.is_facing_polygon(poly2, exact=True):
        case = 1
    elif poly1.area > poly2.area and poly2_points_in_poly1.all():
        case = 2
    elif poly2.area > poly1.area and poly1_points_in_poly2.all():
        case = 3
    else:
        assert (poly1_points_in_poly2.any() or poly2_points_in_poly1.any())
        case = 4  # They must be partially overlapping

    # Slice the facing polygons
    if case == 1:
        # 1) They are matching exactly (all points are equal) -> no slice needed
        return (sld1, sld2)

    elif case == 2:
        # 2) poly1 is bigger, the poly2 polygon is fully within poly1 -> slice poly1
        return _case_2(sld1, poly1, sld2, poly2)

    elif case == 3:
        # 3) poly2 is bigger, the poly1 polygon is fully within poly2 -> slice poly2
        # It is case 3 reversed!
        sld2, sld1 = _case_2(sld2, poly2, sld1, poly1)
        return sld1, sld2

    elif case == 4:
        # 4) They are partially overlapping -> slice both
        return _case_4(sld1, poly1, sld2, poly2)

    else:
        raise NotImplementedError(f"Case {case} was not implemented.")


def find_n_closest_points_between_2_polygons(
    poly1: Polygon,
    poly2: Polygon,
    n: int,
) -> list[tuple[Point, Point]]:
    """Return a list of pairs of closest points between 2 polygons.

    The pairs are sorted based on distance in the ascending order.
    The number of pairs to return is n.
    Each point can be used once, i.e. each pair is unique.
    """
    dist_p1_p2 = {}  # {Point of poly1: (distance, Point of poly2)}
    for p1 in poly1.points:
        if p1 not in dist_p1_p2:
            dist_p1_p2[p1] = []
        for p2 in poly2.points:
            d = length(vector(p1, p2))
            dist_p1_p2[p1].append((d, p2))

    for p1 in dist_p1_p2.keys():
        dist_p1_p2[p1] = sorted(
            dist_p1_p2[p1],
            key=lambda x: x[0],  # sort by distance (first element of the tuple)
        )

    pairs = []
    points_used = set()
    for p1, closest in dist_p1_p2.items():
        _, closest_p2 = closest[0]
        if p1 not in points_used and closest_p2 not in points_used:
            pairs.append((p1, closest_p2))
            points_used.add(p1)
            points_used.add(closest_p2)

        if len(pairs) == n:
            # Just n pairs was requested
            break

    return pairs


def replace_polygons_in_solid(sld: Solid, to_replace: Polygon, new_polys: list[Polygon]) -> Solid:
    """Replaces a polygon in the solid with a list of new polygons.

    Args:
        sld: solid
        to_replace: polygon to replace
        new_polys: list of new polygons

    Return:
        new solid
    """
    poly_path = sld.find_polygon(to_replace.name)
    parent_wall = poly_path.split(PATH_SEP)[0]  # Parent wall

    walls = sld.get_walls()
    new_walls = []
    for w in walls:
        if w.name != parent_wall:
            new_walls.append(w)
        else:
            polygons = w.get_polygons()
            new_polygons = [p for p in polygons if p.name != to_replace.name]
            new_polygons.extend(new_polys)
            wall = Wall(new_polygons, name=w.name, uid=w.uid)
            new_walls.append(wall)

    sld_new = Solid(new_walls, name=sld.name, uid=sld.uid)
    assert np.isclose(sld_new.volume, sld.volume)

    return sld_new

# =============================================
# Auxiliary functions to limit boilerplate code
# =============================================
def _case_2(sld1: Solid, poly1: Polygon, sld2: Solid, poly2: Polygon) -> tuple[Solid, Solid]:
    # 2) poly1 is bigger, the poly2 polygon is fully within poly1 -> slice poly1
    # Divide poly1 into 2 smaller polygons, one of them facing poly2
    slicing_points = [pt for pt in poly2.points if pt not in poly1.points]
    poly1_sup = None  # Placeholder for the supplementary slice (needed in case 2b)

    try:
        # If it is 2b, it will raise GeometryError, because the first and last
        # points do not touch any vertex or edges
        poly1_int, poly1_ext = poly1.slice(
            slicing_points,
            name1 = f"{poly1.name}-1",
            pt1 = poly2.some_interior_point(),
            name2 = f"{poly1.name}-2",
        )

    except GeometryError:
        # If it is 2b, poly1 must be sliced twice.
        # First let's find closest points - they will be used to slice poly1
        pairs = find_n_closest_points_between_2_polygons(poly1, poly2, n=2)

        # Make the supplementary slice of poly1 using the closest points between polygons
        # [poly1 vertex 1, poly2 vertex 1, poly2 vertex 2, poly1 vertex 2]
        sup_slicing_points = [pairs[0][0], pairs[0][1], pairs[1][1], pairs[1][0]]

        ref_poly = Polygon(sup_slicing_points)
        # One of the resulting polygons is likely non-convex,
        # so expect triangulation warning messages during the below operation
        poly1_sup, poly1_main = poly1.slice(
            sup_slicing_points,
            name1 = f"{poly1.name}-sup",
            pt1 = ref_poly.some_interior_point(),
            name2 = f"{poly1.name}-main",  # This one will be sliced further
        )

        # Make the main slice, needed to stitch poly2 to poly1
        # One of the resulting polygons is likely non-convex,
        # so expect triangulation warning messages during the below operation
        num_tries = 0
        max_tries = len(slicing_points)
        while True:
            try:
                poly1_int, poly1_ext = poly1_main.slice(
                    slicing_points,
                    name1 = f"{poly1.name}-{poly2.name}",
                    pt1 = poly2.some_interior_point(),
                    name2 = f"{poly1.name}",
                )
                break
            except GeometryError as err:
                slicing_points = roll_back(slicing_points)
                num_tries += 1
                if num_tries > max_tries:
                    raise err

    # Replace poly1 with the new polygons
    new_polys = [poly1_ext, poly1_int]
    if poly1_sup is not None:
        new_polys.append(poly1_sup)

    sld1_new = replace_polygons_in_solid(sld1, to_replace=poly1, new_polys=new_polys)

    return sld1_new, sld2


def _case_4(sld1: Solid, poly1: Polygon, sld2: Solid, poly2: Polygon) -> tuple[Solid, Solid]:
    # 4) They are partially overlapping -> slice both
    # TODO: This function should be tested with polygons with more vertices (than 4)

    # Need to use line_segment_intersection() to find slicing points
    # Slicing poly2 is similar to slicing poly1 (symmetry)
    def slice_a_using_b(sld_a, poly_a, poly_b):
        slicing_poly_a = []
        added = set()
        for pab, pbb in poly_b.edges:
            for paa, pba in poly_a.edges:
                pcross = line_segment_intersection(pab, pbb, paa, pba)
                if pcross is None:
                    continue
                else:
                    if pcross not in added and pcross not in poly_a.points:
                        slicing_poly_a.append(pcross)
                        added.add(pcross)
            if pbb not in added:
                if poly_a.is_point_inside(pbb):
                    slicing_poly_a.append(pbb)
                    added.add(pbb)

        # Try slicing poly_a
        poly_a_int, poly_a_ext = None, None
        num_tries = 0
        max_num_tries = len(slicing_poly_a)
        while num_tries < max_num_tries:
            try:
                poly_a_int, poly_a_ext = poly_a.slice(slicing_poly_a)
                break  # Slicing successful
            except GeometryError as err:
                # Slicing unsuccessful, will try to shift the points
                # until the first slicing point is at the edge or vertex
                if num_tries >= max_num_tries:
                    raise err
                slicing_poly_a = roll_back(slicing_poly_a)
            num_tries += 1

        if poly_a_int is not None and poly_a_ext is not None:
            sld_a_new = replace_polygons_in_solid(
                sld_a,
                to_replace=poly_a,
                new_polys=[poly_a_int, poly_a_ext],
            )
        else:
            raise ValueError(f"New polygons not assigned, so cannot replace {poly_a} in {sld_a}")

        return sld_a_new

    sld1_new = slice_a_using_b(sld1, poly1, poly2)
    sld2_new = slice_a_using_b(sld2, poly2, poly1)

    return sld1_new, sld2_new
