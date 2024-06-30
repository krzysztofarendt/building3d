from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.mesh.mesh import Mesh
from building3d.mesh.quality.mesh_stats import mesh_stats


def test_mesh_stats():
    solid = box(1, 1, 1)
    zone = Zone()
    zone.add_solid(solid)
    mesh = Mesh(delta=0.3)
    mesh.add_zone(zone)
    mesh.generate(solidmesh=True)

    # Stats for PolyMesh
    vertices, elements = mesh.polymesh.vertices, mesh.polymesh.faces
    stats = mesh_stats(vertices, elements)
    assert "PolyMesh statistics" in stats

    # Stats for polymesh
    vertices, elements = mesh.solidmesh.vertices, mesh.solidmesh.elements
    stats = mesh_stats(vertices, elements)
    assert "SolidMesh statistics" in stats
