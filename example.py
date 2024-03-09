from building3d.display.plot_space import plot_space
from building3d.geom.point import Point
from building3d.geom.space import Space
from building3d.geom.wall import Wall


def example():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 2.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall("floor", [p0, p3, p2, p1])
    wall0 = Wall("wall0", [p0, p1, p5, p4])
    wall1 = Wall("wall1", [p1, p2, p6, p5])
    wall2 = Wall("wall2", [p3, p7, p6, p2])
    wall3 = Wall("wall3", [p0, p4, p7, p3])
    ceiling = Wall("ceiling", [p4, p5, p6, p7])

    room = Space("room", [floor, wall0, wall1, wall2, wall3, ceiling])
    room.verify()

    plot_space(room)

    return 0


if __name__ == "__main__":
    example()
