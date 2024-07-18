from building3d.geom.building import Building
from building3d.geom.solid import Solid
from building3d.geom.point import Point


def get_location(p: Point, last_known_solid: str, building: Building) -> str:
    """Return path to solid having the point `p`.

    Args:
        p: considered point
        last_known_solid: path to the last location (solid)
        building: considered building

    Return:
        path to current solid, e.g. "zone_name/solid_name"
    """
    solids_to_search = [last_known_solid]
    solids_to_search += building.find_adjacent_solids()[last_known_solid]

    location = ""

    found = False

    for path_to_solid in solids_to_search:
        s = building.get_object(path_to_solid)

        if isinstance(s, Solid):
            if s.is_point_inside(p):
                location = path_to_solid

                found = True
                break
        else:
            raise TypeError(f"Incorrect solid type: {s}")

    if not found:
        raise RuntimeError(f"Point outside building: {p}")

    assert len(location) > 0

    return location
