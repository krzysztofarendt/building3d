from mayavi import mlab

from building3d.geom.zone import Zone
from building3d.mesh.mesh import Mesh


def plot_zone(
    zone: Zone,
    mesh: Mesh,
    show_triangulation: bool = True,
    show_normals: bool = True,
    show_mesh: bool = True,
    test: bool = False,
):
    rgb_white = (1, 1, 1)
    rgb_red = (1, 0, 0)
    rgb_blue = (0, 0, 1)
    rgb_green = (0, 1, 0)

    # Plot vertices
    vertices = zone.vertices()
    x = [p.x for p in vertices]
    y = [p.y for p in vertices]
    z = [p.z for p in vertices]

    _ = mlab.points3d(x, y, z, color=rgb_blue, scale_factor=0.1)

    # Plot walls
    for wall in zone.walls:
        x = [p.x for p in wall.points]
        y = [p.y for p in wall.points]
        z = [p.z for p in wall.points]
        tri = wall.triangles
        name = wall.name

        # Plot surfaces
        _ = mlab.triangular_mesh(
            x, y, z, tri,
            name=name,
            opacity=0.5,
            color=rgb_white,
            representation="surface",
        )

        # Plot triangles
        if show_triangulation:
            _ = mlab.triangular_mesh(
                x, y, z, tri,
                name=name,
                line_width=2.0,
                opacity=1.0,
                color=rgb_white,
                representation="wireframe",
            )

        # Plot normals
        if show_normals:
            cx = wall.centroid.x
            cy = wall.centroid.y
            cz = wall.centroid.z
            u, v, w = wall.normal
            _ = mlab.quiver3d(
                cx, cy, cz, u, v, w,
                mode="2darrow",
                color=rgb_red,
            )

    # Plot mesh
    if show_mesh:
        x = [p.x for p in mesh.vertices]
        y = [p.y for p in mesh.vertices]
        z = [p.z for p in mesh.vertices]
        tri = mesh.faces

        # Plot triangles
        _ = mlab.triangular_mesh(
            x, y, z, tri,
            line_width=2.0,
            opacity=0.5,
            color=rgb_green,
            representation="wireframe",
        )
        # Plot surfaces
        _ = mlab.triangular_mesh(
            x, y, z, tri,
            opacity=0.5,
            color=rgb_blue,
            representation="surface",
        )

    if test:
        return
    else:
        mlab.show()
        return
