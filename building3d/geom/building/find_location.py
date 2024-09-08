from building3d.geom.building import Building
from building3d.geom.solid import Solid
from building3d.geom.types import PointType


def find_location(p: PointType, building: Building, *first_look_at: str) -> str:
    """Return path to solid containing the point `p`.

    Args:
        p: considered point
        building: considered building
        *first_look_at: solids to start search with

    Return:
        path to current solid, e.g. "zone_name/solid_name"
    """
    solids_to_search = list(first_look_at)

    for z in building.children.values():
        for s in z.children.values():
            solids_to_search.append(s.path)

    location = ""

    found = False

    for path_to_solid in solids_to_search:
        s = building.get(path_to_solid)

        if isinstance(s, Solid):
            if s.is_point_inside(p):
                location = path_to_solid

                found = True
                break
        else:
            raise TypeError(f"Incorrect solid type: {s}")

    if not found:
        raise RuntimeError(f"Point ({p}) not found in any of the solids of {building}")

    assert len(location) > 0

    return location
