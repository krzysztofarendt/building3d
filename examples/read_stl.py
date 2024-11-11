from building3d.display.plot_objects import plot_objects
from building3d.io.stl import read_stl

if __name__ == "__main__":
    print("This example loads and STL file and plots it on screen")
    teapot = read_stl("resources/stl/utah_teapot.stl")
    plot_objects((teapot,))
