import numpy as np
import pytest

from building3d.config import GEOM_EPSILON
from building3d.geom.predefined.solids.box import box
from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall


def test_correct_space_geometry():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling = Wall([Polygon([p4, p5, p6, p7])])

    _ = Solid([floor, wall0, wall1, wall2, wall3, ceiling])


def test_points_not_shared_by_2_walls():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    p4err = Point(0.0, 0.0, 2.0)
    p5err = Point(1.0, 0.0, 2.0)
    p6err = Point(1.0, 1.0, 2.0)
    p7err = Point(0.0, 1.0, 2.0)

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    # Make ceiling too high (not attached to walls)
    ceiling = Wall([Polygon([p4err, p5err, p6err, p7err])])

    with pytest.raises(GeometryError):
        _ = Solid([floor, wall0, wall1, wall2, wall3, ceiling])


def test_point_inside():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling = Wall([Polygon([p4, p5, p6, p7])])

    sld = Solid([floor, wall0, wall1, wall2, wall3, ceiling])

    ptest = Point(0.5, 0.5, 0.5)
    assert sld.is_point_inside(ptest) is True
    ptest = Point(-0.5, 0.5, 0.5)
    assert sld.is_point_inside(ptest) is False
    ptest = Point(0.0, 0.0, -0.5)
    assert sld.is_point_inside(ptest) is False
    ptest = Point(0.0, 0.0, 0.0)  # This point is in the corner of the solid...
    assert sld.is_point_inside(ptest) is True  # ...we assume it's inside
    assert sld.is_point_at_the_boundary(ptest) is True


def test_bounding_box():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling = Wall([Polygon([p4, p5, p6, p7])])

    sld = Solid([floor, wall0, wall1, wall2, wall3, ceiling])
    pmin, pmax = sld.bounding_box()
    assert pmin.x == 0.0 and pmin.y == 0.0 and pmin.z == 0.0
    assert pmax.x == 1.0 and pmax.y == 1.0 and pmax.z == 1.0


def test_volume():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(2.0, 0.0, 1.0)
    p6 = Point(2.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling = Wall([Polygon([p4, p5, p6, p7])])

    sld = Solid([floor, wall0, wall1, wall2, wall3, ceiling])
    assert np.isclose(sld.volume, 2.0, atol=GEOM_EPSILON)


def test_is_adjacent():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor_1 = Wall([Polygon([p0, p3, p2, p1])])
    wall0_1 = Wall([Polygon([p0, p1, p5, p4])])
    wall1_1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2_1 = Wall([Polygon([p3, p7, p6, p2])])
    wall3_1 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling_1 = Wall([Polygon([p4, p5, p6, p7])])

    sld_1 = Solid([floor_1, wall0_1, wall1_1, wall2_1, wall3_1, ceiling_1])

    move = [1.0, 0.0, 0.0]
    p0 = Point(0.0, 0.0, 0.0) + move
    p1 = Point(1.0, 0.0, 0.0) + move
    p2 = Point(1.0, 1.0, 0.0) + move
    p3 = Point(0.0, 1.0, 0.0) + move
    p4 = Point(0.0, 0.0, 1.0) + move
    p5 = Point(1.0, 0.0, 1.0) + move
    p6 = Point(1.0, 1.0, 1.0) + move
    p7 = Point(0.0, 1.0, 1.0) + move

    floor_2 = Wall([Polygon([p0, p3, p2, p1])])
    wall0_2 = Wall([Polygon([p0, p1, p5, p4])])
    wall1_2 = Wall([Polygon([p1, p2, p6, p5])])
    wall2_2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3_2 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling_2 = Wall([Polygon([p4, p5, p6, p7])])

    sld_2 = Solid([floor_2, wall0_2, wall1_2, wall2_2, wall3_2, ceiling_2])

    move = [2.0, 0.0, 0.0]
    p0 = Point(0.0, 0.0, 0.0) + move
    p1 = Point(1.0, 0.0, 0.0) + move
    p2 = Point(1.0, 1.0, 0.0) + move
    p3 = Point(0.0, 1.0, 0.0) + move
    p4 = Point(0.0, 0.0, 1.0) + move
    p5 = Point(1.0, 0.0, 1.0) + move
    p6 = Point(1.0, 1.0, 1.0) + move
    p7 = Point(0.0, 1.0, 1.0) + move

    floor_3 = Wall([Polygon([p0, p3, p2, p1])])
    wall0_3 = Wall([Polygon([p0, p1, p5, p4])])
    wall1_3 = Wall([Polygon([p1, p2, p6, p5])])
    wall2_3 = Wall([Polygon([p3, p7, p6, p2])])
    wall3_3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling_3 = Wall([Polygon([p4, p5, p6, p7])])

    sld_3 = Solid([floor_3, wall0_3, wall1_3, wall2_3, wall3_3, ceiling_3])

    assert sld_1.is_adjacent_to_solid(sld_2)
    assert sld_2.is_adjacent_to_solid(sld_1)
    assert not sld_1.is_adjacent_to_solid(sld_3)
    assert not sld_3.is_adjacent_to_solid(sld_1)


def test_is_adjacent_exact_false():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor_1 = Wall([Polygon([p0, p3, p2, p1])])
    wall0_1 = Wall([Polygon([p0, p1, p5, p4])])
    wall1_1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2_1 = Wall([Polygon([p3, p7, p6, p2])])
    wall3_1 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling_1 = Wall([Polygon([p4, p5, p6, p7])])
    sld_1 = Solid([floor_1, wall0_1, wall1_1, wall2_1, wall3_1, ceiling_1])

    scale = (2, 2, 2)
    move = (-2, 0, 0)
    p0 = Point(0.0, 0.0, 0.0) * scale + move
    p1 = Point(1.0, 0.0, 0.0) * scale + move
    p2 = Point(1.0, 1.0, 0.0) * scale + move
    p3 = Point(0.0, 1.0, 0.0) * scale + move
    p4 = Point(0.0, 0.0, 1.0) * scale + move
    p5 = Point(1.0, 0.0, 1.0) * scale + move
    p6 = Point(1.0, 1.0, 1.0) * scale + move
    p7 = Point(0.0, 1.0, 1.0) * scale + move

    floor_2 = Wall([Polygon([p0, p3, p2, p1])])
    wall0_2 = Wall([Polygon([p0, p1, p5, p4])])
    wall1_2 = Wall([Polygon([p1, p2, p6, p5])])
    wall2_2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3_2 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling_2 = Wall([Polygon([p4, p5, p6, p7])])
    sld_2 = Solid([floor_2, wall0_2, wall1_2, wall2_2, wall3_2, ceiling_2])

    assert sld_1.is_adjacent_to_solid(sld_2, exact=False)
    assert not sld_2.is_adjacent_to_solid(sld_1)
    assert not sld_2.is_adjacent_to_solid(sld_1, exact=True)

    scale = (2, 2, 2)
    move = (-2.01, 0, 0)  # 1 cm too far to be adjacent
    p0 = Point(0.0, 0.0, 0.0) * scale + move
    p1 = Point(1.0, 0.0, 0.0) * scale + move
    p2 = Point(1.0, 1.0, 0.0) * scale + move
    p3 = Point(0.0, 1.0, 0.0) * scale + move
    p4 = Point(0.0, 0.0, 1.0) * scale + move
    p5 = Point(1.0, 0.0, 1.0) * scale + move
    p6 = Point(1.0, 1.0, 1.0) * scale + move
    p7 = Point(0.0, 1.0, 1.0) * scale + move

    floor_2 = Wall([Polygon([p0, p3, p2, p1])])
    wall0_2 = Wall([Polygon([p0, p1, p5, p4])])
    wall1_2 = Wall([Polygon([p1, p2, p6, p5])])
    wall2_2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3_2 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling_2 = Wall([Polygon([p4, p5, p6, p7])])
    sld_2 = Solid([floor_2, wall0_2, wall1_2, wall2_2, wall3_2, ceiling_2])

    assert not sld_1.is_adjacent_to_solid(sld_2, exact=False)
    assert not sld_2.is_adjacent_to_solid(sld_1)
    assert not sld_2.is_adjacent_to_solid(sld_1, exact=True)


def test_is_adjacent_for_coplanar_but_not_touching():
    # These solids have polygons that are coplanar and with opposite normals
    # but they are not touching, so they are not adjacent
    solid_1 = box(3, 3, 2, (1, 1, 3), name="solid_1")
    solid_2 = box(1, 1, 1, (5, 0, 0), name="solid_2")
    assert solid_1.is_adjacent_to_solid(solid_2, exact=True) is False
    assert solid_1.is_adjacent_to_solid(solid_2, exact=False) is False


def test_equality():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling = Wall([Polygon([p4, p5, p6, p7])])
    sld0 = Solid([floor, wall0, wall1, wall2, wall3, ceiling])
    sld1 = Solid([floor, wall0, wall1, wall2, wall3, ceiling])
    assert sld0 == sld1


def test_solid_get_mesh():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling = Wall([Polygon([p4, p5, p6, p7])])

    walls = [floor, wall0, wall1, wall2, wall3, ceiling]
    sld = Solid(walls)
    verts, faces = sld.get_mesh()

    num_verts, num_faces = 0, 0
    for w in walls:
        v, f = w.get_mesh()
        num_verts += len(v)
        num_faces += len(f)

    assert len(verts) == num_verts
    assert len(faces) == num_faces
