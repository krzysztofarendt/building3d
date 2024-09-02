import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building
from building3d.geom.numba.types import FLOAT


def get_solid(dx=0) -> Solid:
    p0 = new_point(0.0, 0.0, 0.0) + np.array([dx, 0, 0], dtype=FLOAT)
    p1 = new_point(1.0, 0.0, 0.0) + np.array([dx, 0, 0], dtype=FLOAT)
    p2 = new_point(1.0, 1.0, 0.0) + np.array([dx, 0, 0], dtype=FLOAT)
    p3 = new_point(0.0, 1.0, 0.0) + np.array([dx, 0, 0], dtype=FLOAT)
    p4 = new_point(0.0, 0.0, 1.0) + np.array([dx, 0, 0], dtype=FLOAT)
    p5 = new_point(1.0, 0.0, 1.0) + np.array([dx, 0, 0], dtype=FLOAT)
    p6 = new_point(1.0, 1.0, 1.0) + np.array([dx, 0, 0], dtype=FLOAT)
    p7 = new_point(0.0, 1.0, 1.0) + np.array([dx, 0, 0], dtype=FLOAT)

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

    solid = Solid([walls, floor, roof], f"solid{dx}")
    return solid


def get_zone() -> Zone:
    zone = Zone([get_solid(0), get_solid(1)], "zone")
    return zone


def test_building():
    z = get_zone()
    b = Building([z], "building")

    assert list(b.children.values())[0] is z
    assert np.allclose(b.bbox(), [[0, 0, 0], [2, 1, 1]])
    assert b["zone"] is z
    assert isinstance(b["zone"]["solid0"], Solid)
    assert isinstance(b["zone"]["solid0"]["walls"], Wall)
    assert isinstance(b["zone"]["solid0"]["walls"]["w2"], Polygon)

    verts, faces = b.get_mesh()
    assert verts.shape == (2 * 6 * 4, 3)  # NOTE: points not unique
    assert faces.shape == (2 * 12, 3)  # NOTE: points not unique
