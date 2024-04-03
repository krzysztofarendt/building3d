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

    # Plot tetrahedral wireframe  # TODO: The mesh does not look correct
    # Vertices: a, b, c, d
    # Edges:
    # 1. a -> b
    # 2. b -> c
    # 3. c -> a
    # 4. a -> d
    # 5. d -> b
    # 6. c -> d
    if len(mesh.solids) > 0:
        print("Plotting solid mesh wireframe...")
        print(f"{np.array(mesh.sld_mesh_elements).max()=}")
        print(f"{len(mesh.sld_mesh_vertices)=}")
        print(f"{len(mesh.sld_mesh_elements)=}")
        for i, el in enumerate(mesh.sld_mesh_elements):
            a = mesh.sld_mesh_vertices[el[0]]
            b = mesh.sld_mesh_vertices[el[1]]
            c = mesh.sld_mesh_vertices[el[2]]
            d = mesh.sld_mesh_vertices[el[3]]
            edges = [(a, b), (b, c), (c, a), (a, d), (d, b), (c, d)]
            for pair in edges:
                x = [p.x for p in pair]
                y = [p.y for p in pair]
                z = [p.z for p in pair]
                _ = mlab.plot3d(x, y, z)
            print(f"\r{100.0 * (i + 1) / len(mesh.sld_mesh_elements):.2f}%", end="")
        print()

    if show:
        mlab.show()
        return
    else:
        return
