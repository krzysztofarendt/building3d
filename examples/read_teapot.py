from mayavi import mlab

import building3d.logger
from building3d.io.stl import read_stl
from building3d.display.plot_zone import plot_zone


if __name__ == "__main__":
    teapot = read_stl("resources/utah_teapot.stl")
