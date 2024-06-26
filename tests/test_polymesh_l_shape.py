from building3d.display.plot_mesh import plot_mesh
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.triangle import triangle_centroid
from building3d.mesh.polymesh import PolyMesh


def test_polymesh_l_shape(plot=False):
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)

    poly = Polygon([p0, p1, p2, p3, p4, p5])
    mesh = PolyMesh(delta=0.5)
    mesh.add_polygon(poly)
    mesh.generate()

    for f in mesh.faces:
        p0 = mesh.vertices[f[0]]
        p1 = mesh.vertices[f[1]]
        p2 = mesh.vertices[f[2]]
        c = triangle_centroid(p0, p1, p2)
        assert poly.is_point_inside(c), "Face outside polygon!"

    if plot is True:
        plot_mesh(mesh)


if __name__ == "__main__":
    test_polymesh_l_shape(plot=True)
