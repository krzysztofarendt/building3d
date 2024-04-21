from building3d.display.plot_solid import plot_solid
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall


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

    floor = Polygon([p0, p3, p2, p1], "floor")
    wall0 = Polygon([p0, p1, p5, p4], "wall0")
    wall1 = Polygon([p1, p2, p6, p5], "wall1")
    wall2 = Polygon([p3, p7, p6, p2], "wall2")
    wall3 = Polygon([p0, p4, p7, p3], "wall3")
    roof = Polygon([p4, p5, p6, p7], "roof")

    boundary = Wall([floor, wall0, wall1, wall2, wall3, roof])
    room = Solid([boundary], "room")

    # Plot
    plot_solid(room, show=False)
