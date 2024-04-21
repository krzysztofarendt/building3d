from building3d import random_id
from building3d.display.plot_wallmesh import plot_wallmesh
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.triangle import triangle_centroid
from building3d.mesh.wallmesh import WallMesh


def test_wallmesh_l_shape(plot=False):
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)

    poly_1 = Polygon(random_id(), [p0, p1, p2, p3, p4, p5])

    p0 = Point(0.3, 0.3, 0.0)
    p6 = Point(1.5, 0.3, 0.0)
    p7 = Point(0.3, 1.0, 0.0)

    poly_2 = Polygon(random_id(), [p0, p6, p7])

    wall = Wall(random_id())
    wall.add_polygon(poly_1)
    wall.add_polygon(poly_2, parent=poly_1.name)

    mesh = WallMesh(delta=0.3)
    mesh.add_wall(wall)
    mesh.generate(
        fixed_points={
            # poly_1.name: [Point(0.1, 0.0, 0.0), Point(0.2, 0.0, 0.0), Point(0.3, 0.0, 0.0)],
        },
    )

    for f in mesh.faces:
        p0 = mesh.vertices[f[0]]
        p1 = mesh.vertices[f[1]]
        p2 = mesh.vertices[f[2]]
        c = triangle_centroid(p0, p1, p2)
        # assert poly_1.is_point_inside(c), "Face outside polygon!"

    if plot is True:
        plot_wallmesh(mesh, show=True)


if __name__ == "__main__":
    test_wallmesh_l_shape(plot=True)

