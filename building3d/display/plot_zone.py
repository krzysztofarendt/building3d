import pyvista as pv

from building3d.geom.cloud import points_to_array
from building3d.geom.zone import Zone


def plot_zone(zone: Zone):
    verts, faces = zone.get_mesh(children=True)

    # Reformat points and faces
    varr = points_to_array(verts)
    farr = []
    for f in faces:
        farr.extend([3, f[0], f[1], f[2]])

    # Plot with PyVista
    mesh = pv.PolyData(varr, faces=farr)
    mesh.plot(show_edges=True, opacity=0.9)
