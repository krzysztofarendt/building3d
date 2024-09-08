from building3d.geom.paths import PATH_SEP
from building3d.geom.paths.validate_name import validate_name


# TODO: Should include building or make it a simple wrapper over PATH_SEP.join((...))
def object_path(
    zone=None,
    solid=None,
    wall=None,
    poly=None,
) -> str:
    """Return an object path suitable for get_object() methods.

    Args:
        zone: zone instance or None
        solid: solid instance or None
        wall: wall instance or None
        poly: polygon instance or None

    Return:
        object path
    """
    path = ""

    if zone is not None:
        validate_name(zone.name)
        path += zone.name

    if solid is not None:
        validate_name(solid.name)
        if zone is not None:
            path += PATH_SEP
        path += solid.name

    if wall is not None:
        validate_name(wall.name)
        if solid is not None:
            path += PATH_SEP
        path += wall.name

    if poly is not None:
        validate_name(poly.name)
        if wall is not None:
            path += PATH_SEP
        path += poly.name

    return path


def split_path(p: str) -> list:
    object_names = p.split(PATH_SEP)
    if len(object_names) == 0:
        raise ValueError("Incorrect object path (empty)")
    return object_names
