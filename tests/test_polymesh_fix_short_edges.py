import numpy as np

from building3d import random_id
from building3d.config import GEOM_EPSILON
from building3d.display.plot_mesh import plot_mesh
from building3d.display.plot_polygons import plot_polygons
from building3d.geom.point import Point
from building3d.geom.vector import normal
from building3d.geom.wall import Wall
from building3d.mesh.mesh import Mesh


def test_fix_short_edges():
    p0 = Point(0.8, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.8, 3.0, 0.0)
    p3 = Point(0.0, 5.0, 0.0)

    wall = Wall(random_id(), [p0, p1, p2, p3])

    mesh = Mesh()
    mesh.add_polygon(wall)
    mesh.generate()
    mesh.polymesh.collapse_points()
    # plot_polygons([wall])
    # plot_mesh(mesh, interior=False, show=True)

    mesh_stats = mesh.polymesh.mesh_statistics(show=True)
    initial_min_edge_len = mesh_stats["min_edge_len"]
    assert (
        initial_min_edge_len < 0.03
    ), "This test requires initial mesh to have some short edges"

    mesh.polymesh.fix_short_edges(min_length=0.1)
    # plot_polygons([wall])
    # plot_mesh(mesh, interior=False, show=True)

    mesh_stats = mesh.polymesh.mesh_statistics(show=True)
    min_edge_len = mesh_stats["min_edge_len"]
    assert min_edge_len > 0.1, "Fixing mesh edges didn't work"


if __name__ == "__main__":
    test_fix_short_edges()
