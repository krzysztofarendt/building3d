from building3d.geom.building import Building
from building3d.geom.paths import PATH_SEP


def find_transparent(building: Building) -> list[str]:
    """Find and return the list of transparent polygons in the building.

    A polygon is transparent if it separates two adjacent solids within a single zone.
    """
    graph = building.get_graph()

    transparent_polys = []
    added = set()

    for k, v in graph.items():
        if k not in added or v not in added:
            z0, _, _, _ = k.split(PATH_SEP)
            if v is not None:
                z1, _, _, _ = v.split(PATH_SEP)
                # Doesn't have to check if p0 is facing p1,
                # because if they are in the graph, they must be
                if z0 == z1:
                    transparent_polys.extend([k, v])
                    added.add(k)
                    added.add(v)

    return transparent_polys
