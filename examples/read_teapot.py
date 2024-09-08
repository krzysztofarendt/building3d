"""This script does the following:
- Read the Utah teapot STL file.
- Plot the teapot using PyVista.
"""

from building3d.display.plot_objects import plot_objects
from building3d.io.stl import read_stl

if __name__ == "__main__":
    teapot = read_stl("resources/utah_teapot.stl")
    plot_objects((teapot,))
