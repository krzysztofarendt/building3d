"""This script does the following:
- Read the Utah teapot STL file.
- Plot the teapot using PyVista.
"""

import building3d.logger
from building3d.display.plot_zone import plot_zone
from building3d.io.stl import read_stl

if __name__ == "__main__":
    teapot = read_stl("resources/utah_teapot.stl")
    plot_zone(teapot)
