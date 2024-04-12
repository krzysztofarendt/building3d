from mayavi import mlab

from building3d.mesh.mesh import Mesh
from building3d.display.plot_solidmesh import plot_solidmesh
from building3d.display.plot_polymesh import plot_polymesh


def plot_mesh(
    mesh: Mesh,
    boundary: bool = True,
    interior: bool = True,
    show: bool = False,
):
    if boundary is True:
        plot_polymesh(mesh.polymesh)

    if interior is True:
        plot_solidmesh(mesh.solidmesh)

    if show:
        mlab.show()
        return
    else:
        return
