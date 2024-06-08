from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone


def floor_plan(
    plan: list[tuple[float, float]],
    height: float,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_vec: tuple[float, float, float] = (0.0, 0.0, 1.0),
    rot_angle: float = 0.0,
    name: str | None = None,
) -> Zone:
    """Make a zone from a floor plan (list of (x, y) points)."""

    plan = [(float(x), float(y)) for x, y in plan]

    floor_pts = [Point(x, y, 0.0) for x, y in plan]
    ceiling_pts = [Point(x, y, height) for x, y in plan]

    walls = []
    for i in range(len(plan)):
        ths = i  # This point
        nxt = ths + 1  # Next point
        if nxt >= len(plan):
            nxt = 0

        p0 = floor_pts[ths]
        p1 = floor_pts[nxt]
        p2 = ceiling_pts[nxt]
        p3 = ceiling_pts[ths]

        poly = Polygon([p0, p1, p2, p3])
        wall = Wall([poly])
        walls.append(wall)

    floor_poly = Polygon(floor_pts)
    ceiling_poly = Polygon(ceiling_pts)

    floor = Wall([floor_poly])
    ceiling = Wall([ceiling_poly])

    walls.append(floor)
    walls.append(ceiling)

    zone = Zone(name=name)
    # TODO: Assert all polygon normals are pointing outwards the zone
    # TODO: Solid should find polygons with reversed order of vertices and fix it
    zone.add_solid(name=name, walls=walls)

    return zone

