from building3d.geom.paths import PATH_SEP


def validate_name(name: str) -> str:
    if PATH_SEP in name:
        raise ValueError(f"'{PATH_SEP}' not allowed in object names")
    return name
