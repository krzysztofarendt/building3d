import numpy as np

from building3d.config import GEOM_RTOL
from building3d.display.plot_solidmesh import plot_solidmesh
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.mesh.quality.mesh_stats import mesh_stats
from building3d.mesh.quality.min_tetra_volume import minimum_tetra_volume
from building3d.mesh.solidmesh import SolidMesh


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

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    roof = Wall([Polygon([p4, p5, p6, p7])])

    zone = Solid([floor, wall0, wall1, wall2, wall3, roof])

    # Must test multiple times, because mesh generation is random
    for _ in range(10):
        delta = 2.0
        mesh = SolidMesh(delta)
        mesh.add_solid(zone)
        mesh.generate()

        min_el_volume = np.min(mesh.volumes)
        min_allowed_volume = minimum_tetra_volume(delta)
        assert min_el_volume > min_allowed_volume

        if plot:
            plot_solidmesh(mesh, show=True)

        # Assert that the sum of tetrahedra volumes is equal to the zone volume
        tot_volume = np.sum(mesh.volumes)
        assert np.isclose(
            tot_volume, zone.volume, rtol=GEOM_RTOL
        ), f"Mesh volume incorrect {tot_volume} vs. {zone.volume}"


def test_copy(plot=False):
    scale = [5, 5, 5]
    p0 = Point(0.0, 0.0, 0.0) * scale
    p1 = Point(1.0, 0.0, 0.0) * scale
    p2 = Point(1.0, 1.0, 0.0) * scale
    p3 = Point(0.0, 1.0, 0.0) * scale
    p4 = Point(0.0, 0.0, 1.0) * scale
    p5 = Point(1.0, 0.0, 0.5) * scale
    p6 = Point(1.0, 1.0, 1.0) * scale
    p7 = Point(0.0, 1.0, 1.5) * scale

    floor = Wall([Polygon([p0, p3, p2, p1])])
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    wall1 = Wall([Polygon([p1, p2, p6, p5])])
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    roof = Wall([Polygon([p4, p5, p6, p7])])

    zone = Solid([floor, wall0, wall1, wall2, wall3, roof])

    delta = 2.0
    mesh = SolidMesh(delta)
    mesh.add_solid(zone)
    mesh.generate()

    mesh_copy = mesh.copy()
    assert mesh_copy is not mesh
    num_el = len(mesh.elements)
    num_el_copy = len(mesh_copy.elements)
    assert num_el == num_el_copy, f"{num_el=} != {num_el_copy} (should be equal!)"

    print(mesh_stats(mesh.vertices, mesh.elements))

    mesh_copy = mesh.copy(max_vol=0.01)  # Removing degenerate elements
    assert mesh_copy is not mesh
    num_el = len(mesh.elements)
    num_el_copy = len(mesh_copy.elements)
    assert num_el != num_el_copy, f"{num_el=} == {num_el_copy} (should be different!)"

    if plot:
        plot_solidmesh(mesh_copy, show=True)


if __name__ == "__main__":
    test_solidmesh(plot=True)
    test_copy(plot=True)
