from building3d.display.plot_objects import plot_objects
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.operations.hole_polygon import hole_polygon

if __name__ == "__main__":
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2, p3])

    h0 = Point(0.2, 0.2, 0.0)
    h1 = Point(0.8, 0.2, 0.0)
    h2 = Point(0.8, 0.8, 0.0)
    h3 = Point(0.2, 0.8, 0.0)
    hole = Polygon([h0, h1, h2, h3])

    polys = hole_polygon(poly, hole)

    wall = Wall(polys)

    plot_objects((wall,))
