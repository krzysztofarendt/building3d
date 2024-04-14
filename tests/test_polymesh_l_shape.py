from building3d import random_id
from building3d.display.plot_polymesh import plot_polymesh
from building3d.geom.point import Point
from building3d.geom.triangle import triangle_centroid
from building3d.geom.wall import Wall
from building3d.mesh.polymesh import PolyMesh


def test_collapse_points(plot=False):
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)

    poly = Wall(random_id(), [p0, p1, p2, p3, p4, p5])
    mesh = PolyMesh()
    mesh.add_polygon(poly)
    mesh.generate()

    for f in mesh.faces:
        p0 = mesh.vertices[f[0]]
        p1 = mesh.vertices[f[1]]
        p2 = mesh.vertices[f[2]]
        c = triangle_centroid(p0, p1, p2)
        assert poly.is_point_inside(c), "Face outside polygon!"

    if plot is True:
        plot_polymesh(mesh, show=True)


if __name__ == "__main__":
    test_collapse_points(plot=True)
