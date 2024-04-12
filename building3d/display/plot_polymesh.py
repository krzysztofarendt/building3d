from mayavi import mlab

from building3d.mesh.exceptions import MeshError
from building3d.mesh.polymesh import PolyMesh
import building3d.display.colors as colors


def plot_polymesh(
    mesh: PolyMesh,
    show: bool = False,
):
    if len(mesh.polygons) <= 0:
        raise MeshError("plot_mesh(..., boundary=True, ...) but PolyMesh empty")
    x = [p.x for p in mesh.vertices]
    y = [p.y for p in mesh.vertices]
    z = [p.z for p in mesh.vertices]
    tri = mesh.faces

    # Plot triangles
    _ = mlab.triangular_mesh(
        x, y, z, tri,
        line_width=2.0,
        opacity=0.5,
        color=colors.RGB_GREEN,
        representation="wireframe",
    )

    # Plot surfaces
    _ = mlab.triangular_mesh(
        x, y, z, tri,
        opacity=0.5,
        color=colors.RGB_BLUE,
        representation="surface",
    )

    if show:
        mlab.show()
        return
    else:
        return

