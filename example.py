from building3d.display.plot_solid import plot_solid
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.point import Point
from building3d.geom.solid import Solid
from building3d.geom.polygon import Polygon
from building3d.mesh.mesh import Mesh


def example():
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

    floor = Polygon("floor", [p0, p3, p2, p1])
    wall0 = Polygon("wall0", [p0, p1, p5, p4])
    wall1 = Polygon("wall1", [p1, p2, p6, p5])
    wall2 = Polygon("wall2", [p3, p7, p6, p2])
    wall3 = Polygon("wall3", [p0, p4, p7, p3])
    roof = Polygon("roof", [p4, p5, p6, p7])

    room = Solid("room", [floor, wall0, wall1, wall2, wall3, roof])
    print(room)

    mesh = Mesh()
    # Polygons do not need to be added manually, because
    # they are taken from the room zone
    mesh.add_polygon(floor)
    mesh.add_polygon(wall0)
    mesh.add_polygon(wall1)
    mesh.add_polygon(wall2)
    mesh.add_polygon(wall3)
    mesh.add_polygon(roof)
    mesh.add_solid(room)

    mesh.generate()
    mesh.polymesh.mesh_statistics(show=True)
    mesh.solidmesh.mesh_statistics(show=True)
    # mesh.solidmesh = mesh.solidmesh.copy(max_vol=0.06)

    # Plot
    plot_solid(room, show_triangulation=True, show_normals=True, show=False)
    plot_mesh(mesh, boundary=True, interior=True, show=True)


if __name__ == "__main__":
    example()
