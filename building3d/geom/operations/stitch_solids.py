import numpy as np

from building3d.geom.paths import PATH_SEP
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.exceptions import GeometryError


def stitch_solids(
    sld1: Solid,
    sld2: Solid,
) -> tuple[Solid, Solid]:

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
    # 3) poly2 is bigger, the poly1 polygon is fully within poly2 -> slice poly2
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
        assert poly1_points_in_poly2.any()
        assert poly2_points_in_poly1.any()
        case = 4  # They must be partially overlapping

    # Slice the facing polygons
    if case == 1:
        # 1) They are matching exactly (all points are equal) -> no slice needed
        return (sld1, sld2)

    elif case == 2:
        # 2) poly1 is bigger, the poly2 polygon is fully within poly1 -> slice poly1
        # Divide poly1 into 2 smaller polygons, one of them facing poly2
        slicing_points = [pt for pt in poly2.points if pt not in poly1.points]
        poly1_int, poly1_ext = poly1.slice(slicing_points)  # TODO: Add interior points and names

        # Replance poly1 with the new polygons
        poly_path = sld1.find_polygon(poly1.name)
        parent_wall = poly_path.split(PATH_SEP)[0]  # Parent wall

        walls = sld1.get_walls()
        new_walls = []
        for w in walls:
            if w.name != parent_wall:
                new_walls.append(w)
            else:
                polygons = w.get_polygons()
                new_polygons = [p for p in polygons if p.name != poly1.name]
                new_polygons.extend([poly1_ext, poly1_int])
                wall = Wall(new_polygons, name=w.name, uid=w.uid)
                new_walls.append(wall)

        sld1 = Solid(walls, name=sld1.name, uid=sld1.uid)

        return sld1, sld2  # TODO: Unit test needed

    elif case == 3:
        # 3) poly2 is bigger, the poly1 polygon is fully within poly2 -> slice poly2
        ...  # TODO: Almost the same as case2 -> re-use the code
        raise NotImplementedError(f"Case {case} was not implemented.")

    elif case == 4:
        # 4) They are partially overlapping -> slice both
        ...
        raise NotImplementedError(f"Case {case} was not implemented.")

    else:
        raise NotImplementedError(f"Case {case} was not implemented.")
