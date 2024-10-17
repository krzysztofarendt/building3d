from building3d.geom.polygon import Polygon

from .imprint_polygon import imprint_polygon


def hole_polygon(poly: Polygon, hole: Polygon) -> list[Polygon]:
    """Make a hole in `poly`. Return resulting polygons.

    The return type is list, because polygons are not allowed to have holes.
    The hole must be first imprinted and then removed.
    """
    polys = imprint_polygon(poly, hole)
    polys = polys[1:]  # Hole is returned as the first one, so we omit it
    return polys
