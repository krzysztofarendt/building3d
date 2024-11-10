import numpy as np

from building3d.geom.points import new_point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.solid.stitch import stitch_solids
from building3d.geom.types import FLOAT
from building3d.geom.wall import Wall


def get_walls(size=1.0, dx=0.0, dy=0.0, dz=0.0) -> tuple[Wall, ...]:
    p0 = new_point(0.0, 0.0, 0.0) + np.array([dx, dy, dz], dtype=FLOAT)
    p1 = new_point(size, 0.0, 0.0) + np.array([dx, dy, dz], dtype=FLOAT)
    p2 = new_point(size, size, 0.0) + np.array([dx, dy, dz], dtype=FLOAT)
    p3 = new_point(0.0, size, 0.0) + np.array([dx, dy, dz], dtype=FLOAT)
    p4 = new_point(0.0, 0.0, size) + np.array([dx, dy, dz], dtype=FLOAT)
    p5 = new_point(size, 0.0, size) + np.array([dx, dy, dz], dtype=FLOAT)
    p6 = new_point(size, size, size) + np.array([dx, dy, dz], dtype=FLOAT)
    p7 = new_point(0.0, size, size) + np.array([dx, dy, dz], dtype=FLOAT)

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

    floor = Wall([poly_floor], name="floor")
    roof = Wall([poly_roof], name="roof")

    return walls, floor, roof


def test_stitch_solids(show=False):
    w0 = get_walls()
    s0 = Solid(w0, "s0")

    w1 = get_walls(dx=1.0, dy=0.5)
    s1 = Solid(w1, "s1")

    w2 = get_walls(dx=2.0, dy=1.0)
    s2 = Solid(w2, "s2")

    w3 = get_walls(size=0.5, dx=0.5, dy=1.0, dz=0.75)
    s3 = Solid(w3, "s3")

    w4 = get_walls(size=0.5, dx=0.25, dy=0.25, dz=1.0)
    s4 = Solid(w4, "s4")  # On top of s0, smaller and in the middle

    w5 = get_walls(size=0.5, dx=-0.5, dy=0.5, dz=0.0)
    s5 = Solid(w5, "s5")

    w6 = get_walls(size=0.5, dx=-0.5, dy=-0.25, dz=-0.25)
    s6 = Solid(w6, "s6")

    stitch_solids(s0, s1)
    stitch_solids(s0, s3)
    stitch_solids(s1, s2)
    stitch_solids(s1, s3)
    stitch_solids(s4, s0)
    stitch_solids(s0, s5)
    stitch_solids(s0, s6)

    assert s0.has_correct_interface(s1)
    assert s0.has_correct_interface(s3)
    assert s1.has_correct_interface(s2)
    assert s1.has_correct_interface(s3)
    assert s4.has_correct_interface(s0)
    assert s0.has_correct_interface(s5)
    assert s0.has_correct_interface(s6)

    if show:
        return s0, s1, s2, s3, s4, s5, s6


if __name__ == "__main__":
    from building3d.display.plot_objects import plot_objects

    s = test_stitch_solids(show=True)
    assert s is not None
    plot_objects(s)
