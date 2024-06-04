import building3d.logger
from building3d.display.plot_building import plot_building
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.mesh.quality.mesh_stats import mesh_stats


def example_1():
    size = 3
    stretch = [size, size, size]
    translate = [3.0, 3.0, 3.0]
    p0 = Point(0.0, 0.0, 0.0) * stretch + translate
    p1 = Point(1.0, 0.0, 0.0) * stretch + translate
    p2 = Point(1.0, 1.0, 0.0) * stretch + translate
    p3 = Point(0.0, 1.0, 0.0) * stretch + translate
    p4 = Point(0.0, 0.0, 1.0) * stretch + translate
    p5 = Point(1.0, 0.0, 0.5) * stretch + translate
    p6 = Point(1.0, 1.0, 1.0) * stretch + translate
    p7 = Point(0.0, 1.0, 1.5) * stretch + translate

    poly_floor = Polygon([p0, p3, p2, p1])
    poly_wall0 = Polygon([p0, p1, p5, p4])
    poly_wall1 = Polygon([p1, p2, p6, p5])
    poly_wall2 = Polygon([p3, p7, p6, p2])
    poly_wall3 = Polygon([p0, p4, p7, p3])
    poly_roof = Polygon([p4, p5, p6, p7])

    walls = Wall(name="walls")
    walls.add_polygon(poly_wall0)
    walls.add_polygon(poly_wall1)
    walls.add_polygon(poly_wall2)
    walls.add_polygon(poly_wall3)

    floor = Wall(name="floor")
    floor.add_polygon(poly_floor)

    roof = Wall(name="roof")
    roof.add_polygon(poly_roof)

    zone = Zone(name="zone")
    zone.add_solid("room", [floor, walls, roof])

    building = Building()
    building.add_zone_instance(zone)
    building.generate_simulation_mesh(delta=0.5, include_volumes=True)

    print(mesh_stats(building.mesh.polymesh.vertices, building.mesh.polymesh.faces))
    print(
        mesh_stats(building.mesh.solidmesh.vertices, building.mesh.solidmesh.elements)
    )
    # mesh.solidmesh = mesh.solidmesh.copy(max_vol=0.06)

    # Plotting examples
    plot_building(building)
    plot_mesh(building.mesh)
    plot_mesh(building.mesh.polymesh)
    plot_mesh(building.mesh.solidmesh, clip=(0.5, 0.5, 0.5))
    plot_mesh(building.mesh.solidmesh, clip="x")


if __name__ == "__main__":
    example_1()
