"""This script does the following:
- Read the Utah teapot STL file.
- Plot the teapot using PyVista.
"""
import pyvista as pv

import building3d.logger
from building3d.io.stl import read_stl
from building3d.geom.cloud import points_to_array


if __name__ == "__main__":
    # Read STL
    teapot = read_stl("resources/utah_teapot.stl", verify=False)
    verts, faces = teapot.get_mesh()

    # Reformat points and faces
    varr = points_to_array(verts)
    farr = []
    for f in faces:
        farr.extend([3, f[0], f[1], f[2]])

    # Plot with PyVista
    mesh = pv.PolyData(varr, faces=farr)
    mesh.plot()
