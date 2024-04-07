from mayavi import mlab

from building3d.mesh.exceptions import MeshError
from building3d.mesh.mesh import Mesh
import building3d.display.colors as colors


def plot_mesh(
    mesh: Mesh,
    boundary: bool = True,
    interior: bool = True,
    show: bool = False,
):
    if boundary is True:
        if len(mesh.polymesh.polygons) <= 0:
            raise MeshError("plot_mesh(..., boundary=True, ...) but PolyMesh empty")
        x = [p.x for p in mesh.polymesh.mesh_vertices]
        y = [p.y for p in mesh.polymesh.mesh_vertices]
        z = [p.z for p in mesh.polymesh.mesh_vertices]
        tri = mesh.polymesh.mesh_faces

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

    if interior is True:
        # Plot tetrahedral wireframe
        # Vertices: a, b, c, d
        # Edges:
        # 1. a -> b
        # 2. b -> c
        # 3. c -> a
        # 4. a -> d
        # 5. d -> b
        # 6. c -> d
        if len(mesh.solidmesh.solids) <= 0:
            raise MeshError("plot_mesh(..., interior=True, ...) but SolidMesh empty")
        done_edges = []
        done_vertices = set()
        for i, el in enumerate(mesh.solidmesh.mesh_elements):
            a = mesh.solidmesh.mesh_vertices[el[0]]
            b = mesh.solidmesh.mesh_vertices[el[1]]
            c = mesh.solidmesh.mesh_vertices[el[2]]
            d = mesh.solidmesh.mesh_vertices[el[3]]
            edges = [(a, b), (b, c), (c, a), (a, d), (d, b), (c, d)]
            for pair in edges:
                if set(pair) not in done_edges:
                    x = [p.x for p in pair]
                    y = [p.y for p in pair]
                    z = [p.z for p in pair]
                    _ = mlab.plot3d(x, y, z, line_width=0.1)
                    for xi, yi, zi in zip(x, y, z):
                        if (xi, yi, zi) not in done_vertices:
                            _ = mlab.points3d(xi, yi, zi, color=colors.RGB_BLUE, scale_factor=0.2)
                            done_vertices.add((xi, yi, zi))

                    done_edges.append(set(pair))
            print(f"\r{100.0 * (i + 1) / len(mesh.solidmesh.mesh_elements):.0f}%", end="")
        print()

    if show:
        mlab.show()
        return
    else:
        return
