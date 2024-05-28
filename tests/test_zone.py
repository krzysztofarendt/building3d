from building3d.geom.predefined.box import box
from building3d.mesh.quality.collapse_points import collapse_points


def test_zone_get_mesh():
    zone = box(1, 1, 1)
    verts, faces = zone.get_mesh()
    assert len(faces) == 6 * 2
    assert len(verts) == 6 * 4

    col_verts, col_faces = collapse_points(verts, faces)
    assert len(col_faces) == len(faces)
    assert len(col_verts) == 8
