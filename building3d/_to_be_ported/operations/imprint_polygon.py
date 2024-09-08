from building3d.util.roll_back import roll_back
from building3d.geom.polygon import Polygon
from building3d.geom.exceptions import GeometryError
from building3d.geom.operations.stitch_solids import (
    find_n_closest_points_between_2_polygons,
)


def imprint_polygon(poly_ext: Polygon, poly_int: Polygon) -> list[Polygon]:
    """Add a subpolygon `poly_int`, cut `poly_ext` into more subpolygons if needed.

    The returned list starts with `poly_int`, followed by one or two polygons
    made from `poly_ext`.
    """

    # poly_ext is bigger, poly_int is fully within poly_ext -> slice poly_ext
    # Divide poly_ext into 2 smaller polygons, one of them facing poly_int
    slicing_points = [pt for pt in poly_int.points if pt not in poly_ext.points]

    ret_polygons = []

    # User can define poly_ext and poly_int with any vertex ordering
    # but depending on the case (poly_int touching edges of poly_ext or not)
    # different orderings may be needed. That's why we try different combinations
    # until the correct one is found.
    try:
        # First let's assume that poly_int is touching some edge of poly_ext...
        num_tries = 0
        max_tries = len(slicing_points)

        while num_tries < max_tries:
            try:
                # If poly_int points are not valid slicing points,
                # it will raise GeometryError
                ref_poly = Polygon(slicing_points)
                poly_ext_int, poly_ext_ext = poly_ext.slice(
                    slicing_points,
                    name1=f"{poly_ext.name}-1",
                    pt1=ref_poly.some_interior_point(),
                    name2=f"{poly_ext.name}-2",
                )
                ret_polygons = [poly_ext_int, poly_ext_ext]
                break

            except GeometryError as err:
                slicing_points = roll_back(slicing_points)
                num_tries += 1
                if num_tries >= max_tries:
                    raise err

    except GeometryError:
        # poly_ext must be sliced twice, because poly_int is not touching any edge
        # Let's find closest points - they will be used to slice poly_ext
        pairs = find_n_closest_points_between_2_polygons(poly_ext, poly_int, n=2)

        # Make the supplementary slice of poly_ext using the closest points between polygons
        # [poly_ext vertex 1, poly_int vertex 1, poly_int vertex 2, poly_ext vertex 2]
        sup_slicing_points = [pairs[0][0], pairs[0][1], pairs[1][1], pairs[1][0]]

        ref_poly = Polygon(sup_slicing_points)
        # One of the resulting polygons is likely non-convex,
        # so expect triangulation warning messages during the below operation
        poly_ext_sup, poly_ext_main = poly_ext.slice(
            sup_slicing_points,
            name1=f"{poly_ext.name}-sup",
            pt1=ref_poly.some_interior_point(),
            name2=f"{poly_ext.name}-main",  # This one will be sliced further
        )

        ref_poly = Polygon(slicing_points)

        num_tries = 0
        max_tries = len(slicing_points)
        while True:
            try:
                # One of the resulting polygons is likely non-convex,
                # so expect triangulation warning messages during the below operation
                poly_ext_int, poly_ext_ext = poly_ext_main.slice(
                    slicing_points,
                    name1=f"{poly_ext.name}-{poly_int.name}",
                    pt1=ref_poly.some_interior_point(),
                    name2=f"{poly_ext.name}",
                )
                ret_polygons = [poly_ext_int, poly_ext_sup, poly_ext_ext]
                break

            except GeometryError as err:
                slicing_points = roll_back(slicing_points)
                num_tries += 1
                if num_tries > max_tries:
                    raise err

    return ret_polygons
