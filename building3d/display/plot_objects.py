import numpy as np
import pyvista as pv

from building3d.geom.cloud import points_to_array


def random_rgb_color() -> list[float]:
    """Return a random RGB color for the PyVista plotter."""
    return np.random.random(3).tolist()


def plot_objects(*objects):
    """Plot multiple objects (like Building, Zone, Solid, Wall).

    The objects must have a method `get_mesh()` which returns `(vertices, faces)`.
    `faces` can be None. In such case, only `vertices` are plotted.
    """
    pl = pv.Plotter()

    for obj in objects:
        verts, faces = obj.get_mesh(children=True)
        varr = points_to_array(verts)
        if faces is not None and len(faces) > 0:
            farr = []
            for f in faces:
                farr.extend([3, f[0], f[1], f[2]])
            mesh = pv.PolyData(varr, faces=farr)
        else:
            mesh = pv.PolyData(varr)

        if len(objects) > 1:
            col = random_rgb_color()
        else:
            col = [1.0, 1.0, 1.0]

        if faces is None or len(faces) == 0:
            pl.add_mesh(mesh, opacity=1.0, point_size=20, color="black")
        else:
            pl.add_mesh(mesh, show_edges=True, opacity=0.7, color=col)

    pl.show()
