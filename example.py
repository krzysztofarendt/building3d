import numpy as np

from building3d.display.plot_zone import plot_zone
from building3d.geom.point import Point
from building3d.geom.zone import Zone
from building3d.geom.wall import Wall
from building3d.geom.vector import length


def example():
    vec = [1, 10, 5]
    p0 = Point(0.0, 0.0, 0.0) * vec
    p1 = Point(1.0, 0.0, 0.0) * vec
    p2 = Point(1.0, 1.0, 0.0) * vec
    p3 = Point(0.0, 1.0, 0.0) * vec
    p4 = Point(0.0, 0.0, 1.0) * vec
    p5 = Point(1.0, 0.0, 0.5) * vec
    p6 = Point(1.0, 1.0, 1.0) * vec
    p7 = Point(0.0, 1.0, 1.5) * vec

    floor = Wall("floor", [p0, p3, p2, p1])
    wall0 = Wall("wall0", [p0, p1, p5, p4])
    wall1 = Wall("wall1", [p1, p2, p6, p5])
    wall2 = Wall("wall2", [p3, p7, p6, p2])
    wall3 = Wall("wall3", [p0, p4, p7, p3])
    roof = Wall("roof", [p4, p5, p6, p7])

    room = Zone("room", [floor, wall0, wall1, wall2, wall3, roof])

    # Verify roof's normal
    print(roof.normal)
    print(roof.centroid)
    print(roof.centroid + roof.normal)
    print(roof.points)
    print(roof.points[1].vector() - roof.points[0].vector())
    print(roof.points[-1].vector() - roof.points[0].vector())

    normal_test = np.cross(
        roof.points[1].vector() - roof.points[0].vector(),
        roof.points[-1].vector() - roof.points[0].vector(),
    )
    normal_test /= length(normal_test)
    print(normal_test)

    # Plot
    plot_zone(room)

    return 0


if __name__ == "__main__":
    example()
