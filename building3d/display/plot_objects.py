import pyvista as pv

from building3d.geom.cloud import points_to_array
from building3d.geom.point import Point
from building3d.display.colors import random_rgb_color


def plot_objects(*objects):
    """Plot multiple objects (like Building, Zone, Solid, Wall, RayCluster).

    The object must have at least one of the following methods:
    - get_mesh(children) - returning points and faces (children=True if include subpolygons)
    - get_lines() - returning points and lines
    - get_points() - returning points
    """
    pl = pv.Plotter()

    for obj in objects:

        # If more than 1 object is given, use different color for each
        if len(objects) > 1:
            col = random_rgb_color()
        else:
            col = [1.0, 1.0, 1.0]

        # Plot mesh, lines, or points, depending on which method is present
        has_get_mesh = callable(getattr(obj, "get_mesh", None))
        has_get_lines = callable(getattr(obj, "get_lines", None))
        has_get_points = callable(getattr(obj, "get_points", None))
        assert has_get_mesh or has_get_lines or has_get_points, f"{obj} has nothing to plot"

        if has_get_mesh:
            verts, faces = obj.get_mesh(children=True)
            varr = points_to_array(verts)
            farr = []
            for f in faces:
                farr.extend([3, f[0], f[1], f[2]])
            mesh = pv.PolyData(varr, faces=farr)
            pl.add_mesh(mesh, show_edges=True, opacity=0.7, color=col)

        if has_get_lines:
            verts, lines = obj.get_lines()
            varr = points_to_array(verts)
            larr = []
            for l in lines:
                larr.extend([len(l)])
                larr.extend(l)
            mesh = pv.PolyData(varr, lines=larr)
            pl.add_mesh(mesh, opacity=0.7, color=col)

        if has_get_points:
            verts = obj.get_points()
            varr = points_to_array(verts)
            mesh = pv.PolyData(varr)
            pl.add_mesh(mesh, opacity=0.9, point_size=5, color=col)

    pl.show()
