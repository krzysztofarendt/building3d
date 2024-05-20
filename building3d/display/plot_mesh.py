import pyvista as pv

from building3d.geom.cloud import points_to_array
from building3d.mesh.mesh import Mesh


def plot_mesh(mesh: Mesh, polygons=True, solids=True):
    polymesh = mesh.polymesh
    poly_verts, poly_els_orig = polymesh.vertices, polymesh.faces
    poly_verts = points_to_array(poly_verts)
    poly_els = []
    for face in poly_els_orig:
        poly_els.extend([3, face[0], face[1], face[2]])

    solidmesh = mesh.solidmesh
    solid_verts, solid_els_orig = solidmesh.vertices, solidmesh.elements
    solid_verts = points_to_array(solid_verts)
    solid_els = []
    for cell in solid_els_orig:
        solid_els.extend([4, cell[0], cell[1], cell[2], cell[3]])

    celltypes = [pv.CellType.TETRA for _ in solid_els_orig]

    grid = pv.UnstructuredGrid(solid_els, celltypes, solid_verts)

    plotter = pv.Plotter()
    plotter.add_mesh(grid, show_edges=True)
    # clipped = grid.clip(normal='x', crinkle=True)
    # plotter.add_mesh(clipped, show_edges=True, opacity=0.6)
    plotter.show()
