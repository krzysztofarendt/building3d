import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.points import new_point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall

if __name__ == "__main__":
    print("This example shows how to create a solid from a set of points.")
    size = 3
    stretch = [size, size, size]
    translate = [3.0, 3.0, 3.0]
    p0 = new_point(0.0, 0.0, 0.0) * stretch + translate
    p1 = new_point(1.0, 0.0, 0.0) * stretch + translate
    p2 = new_point(1.0, 1.0, 0.0) * stretch + translate
    p3 = new_point(0.0, 1.0, 0.0) * stretch + translate
    p4 = new_point(0.0, 0.0, 1.0) * stretch + translate
    p5 = new_point(1.0, 0.0, 0.5) * stretch + translate
    p6 = new_point(1.0, 1.0, 1.0) * stretch + translate
    p7 = new_point(0.0, 1.0, 1.5) * stretch + translate

    poly_floor = Polygon(np.vstack((p0, p3, p2, p1)), name="floor")
    poly_wall0 = Polygon(np.vstack((p0, p1, p5, p4)), name="w0")
    poly_wall1 = Polygon(np.vstack((p1, p2, p6, p5)), name="w1")
    poly_wall2 = Polygon(np.vstack((p3, p7, p6, p2)), name="w2")
    poly_wall3 = Polygon(np.vstack((p0, p4, p7, p3)), name="w3")
    poly_roof = Polygon(np.vstack((p4, p5, p6, p7)), name="roof")

    walls = Wall(name="walls")
    walls.add_polygon(poly_wall0)
    walls.add_polygon(poly_wall1)
    walls.add_polygon(poly_wall2)
    walls.add_polygon(poly_wall3)

    floor = Wall(name="floor")
    floor.add_polygon(poly_floor)

    roof = Wall(name="roof")
    roof.add_polygon(poly_roof)

    solid = Solid(name="room", walls=[walls, floor, roof])

    print("Plot the solid object...")
    plot_objects((solid,))
    print("Plot wall objects...")
    plot_objects((walls, floor, roof))
    print("Plot polygon objects...")
    plot_objects((poly_floor, poly_wall0, poly_wall1, poly_wall2, poly_wall3, poly_roof))
