import numpy as np
import pyvista as pv

from building3d.geom.cloud import points_to_array
from building3d.mesh.mesh import Mesh


def plot_mesh(
    mesh: Mesh,
    polygons: bool = False,  # TODO: not used
    solids: bool = True,    # TODO: not used
    clip: tuple[float, float, float] | str | None = None,
):
    """Plot mesh."""
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

    plotter = pv.Plotter()

    if polygons:
        celltypes = [pv.CellType.TRIANGLE for _ in poly_els_orig]
        grid = pv.UnstructuredGrid(poly_els, celltypes, poly_verts)
        plotter.add_mesh(grid, show_edges=True, opacity=0.75, color="red")

    if solids:
        celltypes = [pv.CellType.TETRA for _ in solid_els_orig]
        grid = pv.UnstructuredGrid(solid_els, celltypes, solid_verts)
        plotter.add_mesh(grid, show_edges=True, opacity=0.75)

        lines = []
        for el in solid_els_orig:
            for i, j in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
                lines.append(solid_verts[el[i]])
                lines.append(solid_verts[el[j]])
        lines = np.array(lines)
        plotter.add_lines(lines, color="gray", width=1.0)

    if clip:
        celltypes = [pv.CellType.TETRA for _ in solid_els_orig]
        grid = pv.UnstructuredGrid(solid_els, celltypes, solid_verts)
        clipped = grid.clip(normal=clip, crinkle=True)
        plotter.add_mesh(clipped, show_edges=True, opacity=1.0, color="green")

    plotter.show()
