from mayavi import mlab

from building3d.geom.solid import Solid
from building3d.display.plot_polygons import plot_polygons
import building3d.display.colors as colors


def plot_solid(
    solid: Solid,
    show_triangulation: bool = True,
    show_normals: bool = True,
    show: bool = False,
):
    # Plot vertices
    vertices = solid.vertices()
    x = [p.x for p in vertices]
    y = [p.y for p in vertices]
    z = [p.z for p in vertices]

    _ = mlab.points3d(x, y, z, color=colors.RGB_BLUE, scale_factor=0.1)

    # Plot walls
    plot_polygons(
        solid.boundary,
        show_triangulation=show_triangulation,
        show_normals=show_normals,
        show=False,
    )

    if show:
        mlab.show()
        return
    else:
        return

