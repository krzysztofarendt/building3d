from mayavi import mlab

from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
import building3d.display.colors as colors


def plot_polygons(
    polygons: list[Polygon] | list[Wall],
    show_triangulation: bool = True,
    show_normals: bool = True,
    show: bool = False,
):
    # Plot vertices
    vertices = []
    for poly in polygons:
        vertices.extend(poly.points)

    x = [p.x for p in vertices]
    y = [p.y for p in vertices]
    z = [p.z for p in vertices]

    _ = mlab.points3d(x, y, z, color=colors.RGB_BLUE, scale_factor=0.1)

    # Plot polygons
    for poly in polygons:
        x = [p.x for p in poly.points]
        y = [p.y for p in poly.points]
        z = [p.z for p in poly.points]
        tri = poly.triangles
        name = poly.name

        # Plot surfaces
        _ = mlab.triangular_mesh(
            x, y, z, tri,
            name=name,
            opacity=0.5,
            color=colors.RGB_WHITE,
            representation="surface",
        )

        # Plot triangles
        if show_triangulation:
            _ = mlab.triangular_mesh(
                x, y, z, tri,
                name=name,
                line_width=2.0,
                opacity=1.0,
                color=colors.RGB_WHITE,
                representation="wireframe",
            )

        # Plot normals
        if show_normals:
            cx = poly.centroid.x
            cy = poly.centroid.y
            cz = poly.centroid.z
            u, v, w = poly.normal
            _ = mlab.quiver3d(
                cx, cy, cz, u, v, w,
                mode="2darrow",
                color=colors.RGB_RED,
            )

    if show:
        mlab.show()
        return
    else:
        return
