from building3d.geom.paths import PATH_SEP


def split_path(p: str) -> list:
    object_names = p.split(PATH_SEP)
    if len(object_names) == 0:
        raise ValueError("Incorrect object path (empty)")
    return object_names
