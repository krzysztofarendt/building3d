from building3d.geom.predefined.box import box
from building3d.mesh.mesh import Mesh
from building3d.mesh.quality.tetra_graph import find_neighbors
from building3d.mesh.quality.tetra_graph import find_neighbors_numba_wrap


def test_mesh_stats():
    zone = box(1, 1, 1)
    mesh = Mesh(delta=0.5)
    mesh.add_zone(zone)
    mesh.generate(solidmesh=True)

    vertices, elements = mesh.solidmesh.vertices, mesh.solidmesh.elements
    neighbors = find_neighbors(vertices, elements)
    neighbors_numba = find_neighbors_numba_wrap(vertices, elements)

    assert neighbors == neighbors_numba
