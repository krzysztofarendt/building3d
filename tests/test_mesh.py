from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.mesh.mesh import Mesh


def test_mesh():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 0.5)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.5)

    floor = Wall(random_id(), [p0, p3, p2, p1])
    wall0 = Wall(random_id(), [p0, p1, p5, p4])
    wall1 = Wall(random_id(), [p1, p2, p6, p5])
    wall2 = Wall(random_id(), [p3, p7, p6, p2])
    wall3 = Wall(random_id(), [p0, p4, p7, p3])
    roof = Wall(random_id(), [p4, p5, p6, p7])

    zone = Zone(random_id(), [floor, wall0, wall1, wall2, wall3, roof])

    delta = 0.5
    mesh = Mesh(delta)
    mesh.add_polygon(floor)
    mesh.add_polygon(wall0)
    mesh.add_polygon(wall1)
    mesh.add_polygon(wall2)
    mesh.add_polygon(wall3)
    mesh.add_polygon(roof)
    mesh.add_solid(zone)
    mesh.generate()

    solidmesh_stats = mesh.solidmesh.mesh_statistics()
    min_vol = delta ** 3 / 50.0
    assert solidmesh_stats["min_tetrahedron_volume"] > min_vol

    polymesh_stats = mesh.polymesh.mesh_statistics()
    min_area = delta ** 2 / 10.0
    assert polymesh_stats["min_face_area"] > min_area
