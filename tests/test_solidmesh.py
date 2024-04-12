from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.mesh.solidmesh import SolidMesh
from building3d.display.plot_solidmesh import plot_solidmesh


def test_solidmesh(plot=False):
    scale = [5, 5, 5]
    p0 = Point(0.0, 0.0, 0.0) * scale
    p1 = Point(1.0, 0.0, 0.0) * scale
    p2 = Point(1.0, 1.0, 0.0) * scale
    p3 = Point(0.0, 1.0, 0.0) * scale
    p4 = Point(0.0, 0.0, 1.0) * scale
    p5 = Point(1.0, 0.0, 0.5) * scale
    p6 = Point(1.0, 1.0, 1.0) * scale
    p7 = Point(0.0, 1.0, 1.5) * scale

    floor = Wall(random_id(), [p0, p3, p2, p1])
    wall0 = Wall(random_id(), [p0, p1, p5, p4])
    wall1 = Wall(random_id(), [p1, p2, p6, p5])
    wall2 = Wall(random_id(), [p3, p7, p6, p2])
    wall3 = Wall(random_id(), [p0, p4, p7, p3])
    roof = Wall(random_id(), [p4, p5, p6, p7])

    zone = Zone(random_id(), [floor, wall0, wall1, wall2, wall3, roof])

    delta = 2.0
    mesh = SolidMesh(delta)
    mesh.add_solid(zone)
    mesh.generate()

    stats = mesh.mesh_statistics()
    min_vol = delta**3 / 50.0
    assert stats["min_tetrahedron_volume"] > min_vol

    if plot:
        plot_solidmesh(mesh, show=True)


if __name__ == "__main__":
    test_solidmesh(plot=True)
