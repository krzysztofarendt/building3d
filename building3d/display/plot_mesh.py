import numpy as np
from mayavi import mlab

from building3d.mesh.mesh import Mesh
import building3d.display.colors as colors


def plot_mesh(
    mesh: Mesh,
    show: bool = False,
):
    x = [p.x for p in mesh.poly_mesh_vertices]
    y = [p.y for p in mesh.poly_mesh_vertices]
    z = [p.z for p in mesh.poly_mesh_vertices]
    tri = mesh.poly_mesh_faces

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

    # Plot tetrahedral wireframe  # TODO
    # print("Plotting solid mesh wireframe...")
    # print(f"{np.array(mesh.elements).max()=}")
    # print(f"{len(mesh.vertices)=}")
    # import pdb; pdb.set_trace()
    # for i, el in enumerate(mesh.elements):
    #     x = [p.x for (i, p) in enumerate(mesh.vertices) if i in el]
    #     y = [p.y for (i, p) in enumerate(mesh.vertices) if i in el]
    #     z = [p.z for (i, p) in enumerate(mesh.vertices) if i in el]
    #     _ = mlab.plot3d(x, y, z)
    #     print(f"\r{i / len(mesh.elements):.2f}%", end="")
    #     if i > 100:
    #         break
    # print()

    if show:
        mlab.show()
        return
    else:
        return
