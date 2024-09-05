from building3d.geom.numba.building import Building
from building3d.geom.numba.building.graph import graph_polygon
from building3d.geom.paths.object_path import split_path


# Use cache to speed up finding transparent polygons for each ray within a building
CACHE = {}  # {id(building): set(transparent_polygon_paths)}


def find_transparent(building: Building) -> set[str]:
    """Finds and returns the list of transparent polygons in the building.

    A polygon is transparent if it separates two adjacent solids within a single zone.

    Args:
        building: Building instance

    Returns:
        set of paths to polygons
    """
    if id(building) in CACHE:
        return CACHE[id(building)]

    else:
        # Find facing polygons (matching exactly)
        graph = graph_polygon(building, facing=True, overlapping=False, touching=False)

        transparent_plg = []
        added = set()

        for k, v in graph.items():
            assert isinstance(v, list)
            assert len(v) <= 1, f"Expected one facing polygon, but found more ({len(v)})"

            if len(v) == 1:
                if k not in added or v[0] not in added:
                    _, z0, _, _, _ = split_path(k)
                    _, z1, _, _, _ = split_path(v[0])

                    # Doesn't have to check if plg0 is facing plg1,
                    # because if they are in the graph, they must be
                    if z0 == z1:
                        transparent_plg.extend([k, v[0]])
                        added.add(k)
                        added.add(v[0])

        # Add to CACHE
        set_of_transparent_polygons = set(transparent_plg)
        CACHE[id(building)] = set_of_transparent_polygons

        return set_of_transparent_polygons
