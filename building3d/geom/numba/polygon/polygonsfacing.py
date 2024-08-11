from building3d.geom.numba.types import PointType, VectorType, IndexType, FLOAT


def are_polygons_facing_each_other(
    pts1: PointType,
    vn1: VectorType,
    pts2: PointType,
    vn2: VectorType,
    exact: bool = True,
) -> bool:
    """Checks if two polygons are facing each other.

    Returns True if all points of two polygons are equal and their normals
    are pointing towards each other.

    If exact is True, all points of two polygons must be equal (order may be different).
    If exact is False, the method checks only if polygons are overlapping, points are coplanar
    and normal vectors are opposite.

    Args:
        poly: another polygon
        exact: if True, all points of adjacent polygons must be equal

    Return:
        True if the polygons are facing each other
    """
    ...

