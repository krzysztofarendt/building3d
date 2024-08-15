import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.types import FLOAT


def get_walls(dx=0) -> tuple[Wall, ...]:
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

    return walls, floor, roof


def test_single_solid():
    walls = get_walls()
    solid = Solid(walls, "solid")
    assert solid.name == "solid"
    assert np.isclose(solid.volume, 1, atol=GEOM_RTOL)
    for i in range(3):
        assert solid.get_walls()[i] is walls[i]
    assert np.allclose(solid.bounding_box(), [[0, 0, 0], [1, 1, 1]])
    assert solid.get_object("walls/w0").name == "w0"
    assert solid.get_object("floor/floor").name == "floor"
    assert isinstance(solid.get_object("floor/floor"), Polygon)
    assert solid.is_point_inside(new_point(0.5, 0.5, 0.5)) is True
    assert solid.is_point_inside(new_point(0.5, 0.5, 0.0)) is True
    assert solid.is_point_inside(new_point(0.0, 0.0, 0.0)) is True
    assert solid.is_point_inside(new_point(0.0, 0.0, -0.1)) is False
    assert solid.is_point_inside(new_point(1.1, 1.1, 1.1)) is False
    assert solid.is_point_at_boundary(new_point(0.0, 0.0, 0.0)) is True
    assert solid.is_point_at_boundary(new_point(0.5, 0.0, 0.5)) is True
    assert solid.is_point_at_boundary(new_point(0.5, 0.5, 0.5)) is False

    verts, faces = solid.get_mesh()
    assert verts.shape == (6 * 4, 3)  # NOTE: points not unique
    assert faces.shape == (12, 3)     # NOTE: points not unique


def test_adjacent_solids():
    walls0 = get_walls(dx=0)
    sld0 = Solid(walls0, "sld0")

    walls1 = get_walls(dx=1)
    sld1 = Solid(walls1, "sld1")

    walls2 = get_walls(dx=2)
    sld2 = Solid(walls2, "sld2")

    assert sld0.is_adjacent_to_solid(sld1) is True
    assert sld1.is_adjacent_to_solid(sld2) is True
    assert sld0.is_adjacent_to_solid(sld2) is False
