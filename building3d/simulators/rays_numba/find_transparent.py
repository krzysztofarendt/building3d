"""
Lines of code, a building's tale,
Transparent polygons we unveil.
From solids and zones, a structure grows,
A cache to speed up what it knows.

Graphs and paths, a complex dance,
Finding faces at a glance.
Adjacent solids, zones align,
Transparent barriers we define.

Python's power, Numba's might,
Building models, day and night.
A script so clever, it does impart,
The essence of the builder's art.

In memory cached, results we keep,
For future queries, fast and deep.
A poem of logic, clean and neat,
This building script, a coding feat.
"""

import logging

from building3d.geom.building import Building
from building3d.geom.building.graph import graph_polygon
from building3d.geom.paths.object_path import split_path


logger = logging.getLogger(__name__)


# Use cache to speed up finding transparent polygons for each ray within a building
CACHE: dict[int, set[str]] = {}  # {id(building): set(transparent_polygon_paths)}


def find_transparent(building: Building) -> set[str]:
    """Finds and returns the list of transparent polygons in the building.

    A polygon is transparent if it separates two adjacent solids within a single zone.

    Args:
        building: Building instance

    Returns:
        set of paths to polygons
    """
    logger.debug(f"Finding transparent polygons in {building.name}")
    if id(building) in CACHE:
        return CACHE[id(building)]

    else:
        # Find facing polygons (matching exactly)
        logger.debug("Making graph")
        graph = graph_polygon(building, facing=True, overlapping=False, touching=False)

        transparent_polygons = []
        added = set()

        logger.debug("Iterating through the graph items")
        for k, v in graph.items():
            assert isinstance(v, list)
            assert (
                len(v) <= 1
            ), f"Expected one facing polygon, but found more ({len(v)})"

            if len(v) == 1:
                if k not in added or v[0] not in added:
                    _, z0, *_ = split_path(k)
                    _, z1, *_ = split_path(v[0])

                    # Doesn't have to check if plg0 is facing plg1,
                    # because if they are in the graph, they must be
                    if z0 == z1:
                        logger.debug(f"Transparent polygons found: {k}, {v[0]}")
                        transparent_polygons.extend([k, v[0]])
                        added.add(k)
                        added.add(v[0])

        # Add to CACHE
        set_of_transparent_polygons = set(transparent_polygons)
        CACHE[id(building)] = set_of_transparent_polygons

        return set_of_transparent_polygons
