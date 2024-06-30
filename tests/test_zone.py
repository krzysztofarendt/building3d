from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.mesh.quality.collapse_points import collapse_points


def test_zone_get_mesh():
    solid = box(1, 1, 1)
    zone = Zone()
    zone.add_solid(solid)
    verts, faces = zone.get_mesh()
    assert len(faces) == 6 * 2
    assert len(verts) == 6 * 4

    col_verts, col_faces = collapse_points(verts, faces)
    assert len(col_faces) == len(faces)
    assert len(col_verts) == 8


def test_equality():
    s1 = box(1, 1, 1)
    s2 = box(1, 1, 1)
    z1 = Zone()
    z2 = Zone()
    z1.add_solid(s1)
    z2.add_solid(s2)

    assert z1 == z2

    s3 = box(1, 1, 1, (1, 1, 1))
    z3 = Zone()
    z3.add_solid(s3)
    assert z1 != z3

    s4 = box(1.0001, 1, 1)
    z4 = Zone()
    z4.add_solid(s4)
    assert z1 != z4
