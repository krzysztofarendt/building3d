from building3d.display.plot_zone import plot_zone
from building3d.geom.point import Point
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.mesh.mesh import Mesh


def test_plot_zone():
    stretch = [10, 8, 5]
    translate = [3.0, 3.0, 3.0]
    p0 = Point(0.0, 0.0, 0.0) * stretch + translate
    p1 = Point(1.0, 0.0, 0.0) * stretch + translate
    p2 = Point(1.0, 1.0, 0.0) * stretch + translate
    p3 = Point(0.0, 1.0, 0.0) * stretch + translate
    p4 = Point(0.0, 0.0, 1.0) * stretch + translate
    p5 = Point(1.0, 0.0, 0.5) * stretch + translate
    p6 = Point(1.0, 1.0, 1.0) * stretch + translate
    p7 = Point(0.0, 1.0, 1.5) * stretch + translate

    floor = Wall("floor", [p0, p3, p2, p1])
    wall0 = Wall("wall0", [p0, p1, p5, p4])
    wall1 = Wall("wall1", [p1, p2, p6, p5])
    wall2 = Wall("wall2", [p3, p7, p6, p2])
    wall3 = Wall("wall3", [p0, p4, p7, p3])
    roof = Wall("roof", [p4, p5, p6, p7])

    mesh = Mesh()
    mesh.add_polygon(floor)
    mesh.add_polygon(wall0)
    mesh.add_polygon(wall1)
    mesh.add_polygon(wall2)
    mesh.add_polygon(wall3)
    mesh.add_polygon(roof)
    mesh.generate()

    room = Zone("room", [floor, wall0, wall1, wall2, wall3, roof])

    # Plot
    plot_zone(room, mesh, test=True)
