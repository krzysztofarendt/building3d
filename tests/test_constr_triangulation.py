from mayavi import mlab

from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.wall import Wall
from building3d.mesh.constrained_triangulation import constr_delaunay_triangulation
from building3d.mesh.triangulation import delaunay_triangulation
from building3d.mesh.polymesh import PolyMesh
from building3d.display.plot_polymesh import plot_polymesh
import building3d.display.colors as colors


def test_constr_triangulation(show=False):
    # Polygon vertices
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)

    poly = Wall(random_id(), [p0, p1, p2, p3, p4, p5])
    delta = 0.5

    # Fixed vertices
    f0 = Point(0.3, 0.0, 0.0)
    f1 = Point(0.4, 0.0, 0.0)
    f2 = Point(0.5, 0.0, 0.0)
    f3 = Point(0.6, 0.0, 0.0)
    f4 = Point(0.5, 0.5, 0.0)
    f5 = Point(1.0, 0.5, 0.0)
    f6 = Point(1.1, 0.6, 0.0)
    f7 = Point(1.2, 0.7, 0.0)
    fix_points = [f0, f1, f2, f3, f4, f5, f6, f7]

    # Standard
    # vertices, faces = delaunay_triangulation(
    #     poly,
    #     delta=delta,
    # )
    # mesh = PolyMesh(delta)
    # mesh.vertices = vertices
    # mesh.faces = faces
    # mesh.polygons = {poly.name: poly}
    # plot_polymesh(mesh, show=show)

    # Constrained
    vertices, faces = constr_delaunay_triangulation(
        poly,
        delta=delta,
        suggest_vertices=[],
        fix_vertices=fix_points,
    )
    mesh = PolyMesh(delta)
    mesh.vertices = vertices
    mesh.faces = faces
    mesh.polygons = {poly.name: poly}
    plot_polymesh(mesh, show=False)

    if show:
        xc = [p.x for p in fix_points]
        yc = [p.y for p in fix_points]
        zc = [p.z for p in fix_points]
        _ = mlab.points3d(xc, yc, zc, color=colors.RGB_RED, scale_factor=0.05)
        mlab.show()


if __name__ == "__main__":
    test_constr_triangulation(show=True)
