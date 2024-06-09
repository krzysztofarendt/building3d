from building3d.display.plot_mesh import plot_mesh
from building3d.display.plot_zone import plot_zone
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.mesh.mesh import Mesh
from building3d.mesh.quality.tetra_graph import find_neighbors
from building3d.mesh.quality.tetra_graph import find_neighbors_numba_wrap


def test_find_neighbors(show=False):
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 0.5)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.5)

    poly_floor = Polygon([p0, p3, p2, p1])
    poly_wall0 = Polygon([p0, p1, p5, p4])
    poly_wall1 = Polygon([p1, p2, p6, p5])
    poly_wall2 = Polygon([p3, p7, p6, p2])
    poly_wall3 = Polygon([p0, p4, p7, p3])
    poly_roof = Polygon([p4, p5, p6, p7])

    walls = Wall(name="walls")
    walls.add_polygon(poly_wall0)
    walls.add_polygon(poly_wall1)
    walls.add_polygon(poly_wall2)
    walls.add_polygon(poly_wall3)

    floor = Wall(name="floor")
    floor.add_polygon(poly_floor)

    roof = Wall(name="roof")
    roof.add_polygon(poly_roof)

    solid = Solid([floor, walls, roof], name="room")

    zone = Zone(name="zone")
    zone.add_solid(solid)

    mesh = Mesh(delta=0.4)
    mesh.add_zone(zone)
    mesh.generate(solidmesh=True)

    vertices = mesh.solidmesh.vertices
    elements = mesh.solidmesh.elements

    neighbors_1 = find_neighbors(vertices, elements)
    neighbors_2 = find_neighbors_numba_wrap(vertices, elements)

    assert (
        neighbors_1 == neighbors_2
    ), "Python and Numba functions returning different results"
    unique_set = set()
    for el in neighbors_2:
        for index in el:
            unique_set.add(index)
    assert len(unique_set) == len(
        elements
    ), "Not all elements used for the neighbor graph"

    if show:
        # Plot
        plot_zone(zone)
        plot_mesh(mesh)


if __name__ == "__main__":
    test_find_neighbors(show=True)
