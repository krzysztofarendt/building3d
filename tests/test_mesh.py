from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.mesh.mesh import Mesh
from building3d.mesh.quality.min_tetra_volume import minimum_tetra_volume
from building3d.mesh.quality.min_triangle_area import minimum_triangle_area


def test_mesh():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 0.5)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.5)

    floor = Wall([Polygon([p0, p3, p2, p1], name="floor")], name="floor")
    wall0 = Wall([Polygon([p0, p1, p5, p4], name="wall0")], name="wall0")
    wall1 = Wall([Polygon([p1, p2, p6, p5], name="wall1")], name="wall1")
    wall2 = Wall([Polygon([p3, p7, p6, p2], name="wall2")], name="wall2")
    wall3 = Wall([Polygon([p0, p4, p7, p3], name="wall3")], name="wall3")
    roof = Wall([Polygon([p4, p5, p6, p7], name="roof")], name="roof")

    solid = Solid([floor, wall0, wall1, wall2, wall3, roof])
    zone = Zone()
    zone.add_solid(solid)
    bdg = Building()
    bdg.add_zone(zone)

    delta = 0.5
    num_tests = 5

    for _ in range(num_tests):
        # Need to repeat this test multiple times, because mesh generation is random
        mesh = Mesh(delta)
        mesh.add_building(bdg)
        mesh.generate(solidmesh=True)

        assert min(mesh.solidmesh.volumes) > minimum_tetra_volume(
            delta
        ), "Min. volume below threshold"
        assert min(mesh.polymesh.areas) > minimum_triangle_area(
            delta
        ), "Min. area below threshold"


def test_mesh_with_subpolygon():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 0.5)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.5)

    floor = Wall([Polygon([p0, p3, p2, p1], name="floor")], name="floor")
    wall0 = Wall([Polygon([p0, p1, p5, p4], name="wall0")], name="wall0")
    wall1 = Wall([Polygon([p1, p2, p6, p5], name="wall1")], name="wall1")
    wall2 = Wall([Polygon([p3, p7, p6, p2], name="wall2")], name="wall2")
    wall3 = Wall([Polygon([p0, p4, p7, p3], name="wall3")], name="wall3")
    roof = Wall([Polygon([p4, p5, p6, p7], name="roof")], name="roof")

    # Subpolygon (parent: floor)
    sp0 = Point(0.2, 0.2, 0.0)
    sp1 = Point(0.8, 0.2, 0.0)
    sp2 = Point(0.8, 0.8, 0.0)
    sp3 = Point(0.0, 0.8, 0.0)
    floor_hole = Polygon([sp0, sp3, sp2, sp1], name="floor_hole")
    floor.add_polygon(floor_hole, parent="floor")

    solid = Solid([floor, wall0, wall1, wall2, wall3, roof], name="solid")
    zone = Zone(name="zone")
    zone.add_solid(solid)
    bdg = Building(name="building")
    bdg.add_zone(zone)

    delta = 0.5
    num_tests = 5

    for _ in range(num_tests):
        # Need to repeat this test multiple times, because mesh generation is random
        mesh = Mesh(delta)
        mesh.add_building(bdg)
        mesh.generate(solidmesh=True)

        assert min(mesh.solidmesh.volumes) > minimum_tetra_volume(
            delta
        ), "Min. volume below threshold"
        assert min(mesh.polymesh.areas) > minimum_triangle_area(
            delta
        ), "Min. area below threshold"
