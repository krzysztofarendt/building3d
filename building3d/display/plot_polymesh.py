from mayavi import mlab

from building3d.mesh.exceptions import MeshError
from building3d.mesh.polymesh import PolyMesh
from building3d.geom.triangle import triangle_centroid
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

    # Plot centroids
    centroids = []
    for f in mesh.faces:
        p0 = mesh.vertices[f[0]]
        p1 = mesh.vertices[f[1]]
        p2 = mesh.vertices[f[2]]
        centroids.append(triangle_centroid(p0, p1, p2))
    xc = [p.x for p in centroids]
    yc = [p.y for p in centroids]
    zc = [p.z for p in centroids]
    _ = mlab.points3d(xc, yc, zc, color=colors.RGB_GREEN, scale_factor=0.05)


    if show:
        mlab.show()
        return
    else:
        return

