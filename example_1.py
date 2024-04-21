from building3d.display.plot_zone import plot_zone
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.mesh.mesh import Mesh


def example_1():
    stretch = [7, 4, 5]
    translate = [3.0, 3.0, 3.0]
    p0 = Point(0.0, 0.0, 0.0) * stretch + translate
    p1 = Point(1.0, 0.0, 0.0) * stretch + translate
    p2 = Point(1.0, 1.0, 0.0) * stretch + translate
    p3 = Point(0.0, 1.0, 0.0) * stretch + translate
    p4 = Point(0.0, 0.0, 1.0) * stretch + translate
    p5 = Point(1.0, 0.0, 0.5) * stretch + translate
    p6 = Point(1.0, 1.0, 1.0) * stretch + translate
    p7 = Point(0.0, 1.0, 1.5) * stretch + translate

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

    zone = Zone(name="zone")
    zone.add_solid("room", [floor, walls, roof])

    mesh = Mesh()
    mesh.add_zone(zone)
    mesh.generate(solidmesh=True)
    mesh.polymesh.mesh_statistics(show=True)
    mesh.solidmesh.mesh_statistics(show=True)
    # mesh.solidmesh = mesh.solidmesh.copy(max_vol=0.06)

    # Plot
    plot_zone(zone, show_triangulation=True, show_normals=True, show=False)
    plot_mesh(mesh, boundary=True, interior=True, show=True)


if __name__ == "__main__":
    example_1()
