import numpy as np

from building3d.display.numba.plot_objects import plot_objects
from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building


if __name__ == "__main__":
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


    poly_floor = Polygon(np.vstack((p0, p3, p2, p1)), name="p_floor")
    poly_wall0 = Polygon(np.vstack((p0, p1, p5, p4)), name="p_0")
    poly_wall1 = Polygon(np.vstack((p1, p2, p6, p5)), name="p_1")
    poly_wall2 = Polygon(np.vstack((p3, p7, p6, p2)), name="p_2")
    poly_wall3 = Polygon(np.vstack((p0, p4, p7, p3)), name="p_3")
    poly_roof = Polygon(np.vstack((p4, p5, p6, p7)), name="p_roof")

    walls = Wall([poly_wall0, poly_wall1, poly_wall2, poly_wall3], name="walls")
    floor = Wall([poly_floor], name="floor")
    roof = Wall([poly_roof], name="roof")
    solid = Solid([walls, floor, roof], name="room")
    zone = Zone([solid], "zone")
    building = Building([zone], "building")

    plot_objects((building, ))
