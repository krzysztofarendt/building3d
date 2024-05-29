import numpy as np
import pyvista as pv

from building3d.geom.cloud import points_to_array
from building3d.mesh.mesh import Mesh
from building3d.mesh.solidmesh import SolidMesh
from building3d.mesh.polymesh import PolyMesh


def plot_mesh(
    mesh: Mesh | SolidMesh | PolyMesh,
    clip: tuple[float, float, float] | str | None = None,
    show: bool = True,
):
    """Plot any type of mesh.

    This function accepts instances of Mesh, SolidMesh, and PolyMesh.
    If the instance type is Mesh, then its SolidMesh is plotted.
    To plot PolyMesh only, you need to explicitly pass PolyMesh.
    """
    if type(mesh) is Mesh:
        # Need to check if the are volume elements in Mesh (or only surface elements)
        if len(mesh.solidmesh.elements) > 0:
            polymesh = None
            solidmesh = mesh.solidmesh
        else:
            polymesh = mesh.polymesh
            solidmesh = None
    elif type(mesh) is PolyMesh:
        polymesh = mesh
        solidmesh = None
    elif type(mesh) is SolidMesh:
        polymesh = None
        solidmesh = mesh
    else:
        raise TypeError(f"Unsupported mesh type: {type(mesh)}")

    plotter = pv.Plotter()

    if polymesh is not None:
        poly_verts, poly_els_orig = polymesh.vertices, polymesh.faces
        poly_verts = points_to_array(poly_verts)
        poly_els = []
        for face in poly_els_orig:
            poly_els.extend([3, face[0], face[1], face[2]])

        celltypes = [pv.CellType.TRIANGLE for _ in poly_els_orig]
        grid = pv.UnstructuredGrid(poly_els, celltypes, poly_verts)
        plotter.add_mesh(grid, show_edges=True, opacity=0.9, color="green")

    if solidmesh is not None:
        solid_verts, solid_els_orig = solidmesh.vertices, solidmesh.elements
        solid_verts = points_to_array(solid_verts)
        solid_els = []
        for cell in solid_els_orig:
            solid_els.extend([4, cell[0], cell[1], cell[2], cell[3]])

        celltypes = [pv.CellType.TETRA for _ in solid_els_orig]
        grid = pv.UnstructuredGrid(solid_els, celltypes, solid_verts)

        if clip:
            celltypes = [pv.CellType.TETRA for _ in solid_els_orig]
            grid = pv.UnstructuredGrid(solid_els, celltypes, solid_verts)
            clipped = grid.clip(normal=clip, crinkle=True)
            plotter.add_mesh(clipped, show_edges=True, opacity=1.0, color="red")

        else:
            plotter.add_mesh(grid, show_edges=True, opacity=0.7, color="yellow")

            lines = []
            for el in solid_els_orig:
                for i, j in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
                    lines.append(solid_verts[el[i]])
                    lines.append(solid_verts[el[j]])
            lines = np.array(lines)
            plotter.add_lines(lines, color="black", width=1.0)

    if show:
        plotter.show()
