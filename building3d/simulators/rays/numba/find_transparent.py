from building3d.geom.numba.building import Building
from building3d.geom.numba.building.graph import graph_polygon
from building3d.geom.paths import PATH_SEP
from building3d.geom.paths.object_path import split_path


def find_transparent(building: Building) -> list[str]:
    """Finds and returns the list of transparent polygons in the building.

    A polygon is transparent if it separates two adjacent solids within a single zone.

    Args:
        building: Building instance

    Returns:
        list of paths to polygons
    """
    # Find facing polygons (matching exactly)
    graph = graph_polygon(building, facing=True, overlapping=False, touching=False)

    transparent_plg = []
    added = set()

    for k, v in graph.items():
        assert isinstance(v, list)
        assert len(v) == 1, f"Expected one facing polygon, but found {len(v)}"

        if k not in added or v[0] not in added:
            bdg0, z0, sld0, wll0, plg0 = split_path(k)
            bdg1, z1, sld1, wll1, plg1 = split_path(v[0])

            # Doesn't have to check if plg0 is facing plg1,
            # because if they are in the graph, they must be
            if z0 == z1:
                transparent_plg.extend([k, v[0]])
                added.add(k)
                added.add(v[0])

    return transparent_plg
