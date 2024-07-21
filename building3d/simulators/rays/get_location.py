from building3d.geom.building import Building
from building3d.geom.solid import Solid
from building3d.geom.point import Point
from building3d.geom.paths.object_path import object_path


def get_location(p: Point, building: Building, *first_look_at: str) -> str:
    """Return path to solid having the point `p`.

    Args:
        p: considered point
        building: considered building
        *first_look_at: solids to start search with

    Return:
        path to current solid, e.g. "zone_name/solid_name"
    """
    solids_to_search = list(first_look_at)

    solids_to_search = []
    for z in building.get_zones():
        for s in z.get_solids():
            s_path = object_path(zone=z, solid=s)
            if s_path not in solids_to_search:
                solids_to_search.append(s_path)

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
        raise RuntimeError(
            f"Point ({p}) not found in any of the solids of {building}")

    assert len(location) > 0

    return location
