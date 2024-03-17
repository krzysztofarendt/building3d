from mayavi import mlab

from building3d.geom.zone import Zone


def plot_zone(
        zone: Zone,
        show_triangulation: bool = True,
        show_normals: bool = True,
):
    rgb_white = (1, 1, 1)
    rgb_red = (1, 0, 0)
    rgb_blue = (0, 0, 1)

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

    mlab.show()
