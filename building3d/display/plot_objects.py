import pyvista as pv

from building3d.geom.cloud import points_to_array


def plot_objects(*objects):
    """Plot multiple objects (like Building, Zone, Solid, Wall).

    The objects must have a method `get_mesh()`.
    """
    verts_all = []
    faces_all = []

    for obj in objects:
        verts, faces = obj.get_mesh(only_parents=False)
        offset = len(verts_all)

        verts_all.extend(verts)
        for f in faces:
            faces_all.append((f[0] + offset, f[1] + offset, f[2] + offset))

    # Reformat points and faces
    varr = points_to_array(verts_all)
    farr = []
    for f in faces_all:
        farr.extend([3, f[0], f[1], f[2]])

    assert len(varr) > 0, "No points available, plotting is impossible"
    assert len(farr) > 0, "No faces specified, plotting is impossible"

    # Plot with PyVista
    mesh = pv.PolyData(varr, faces=farr)
    mesh.plot(show_edges=True, opacity=0.9)
