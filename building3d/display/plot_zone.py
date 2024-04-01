from mayavi import mlab

from building3d.geom.zone import Zone
from building3d.mesh.mesh import Mesh
from building3d.display.plot_polygons import plot_polygons
import building3d.display.colors as colors


def plot_zone(
    zone: Zone,
    mesh: Mesh,
    show_triangulation: bool = True,
    show_normals: bool = True,
    show_mesh: bool = True,
    show: bool = False,
):
    # Plot vertices
    vertices = zone.vertices()
    x = [p.x for p in vertices]
    y = [p.y for p in vertices]
    z = [p.z for p in vertices]

    _ = mlab.points3d(x, y, z, color=colors.RGB_BLUE, scale_factor=0.1)

    # Plot walls
    plot_polygons(zone.walls, mesh=mesh, show=False)

    # Plot tetrahedral wireframe

    if show:
        mlab.show()
        return
    else:
        return

