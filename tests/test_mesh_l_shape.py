from building3d import random_id
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.tetrahedron import tetrahedron_centroid
from building3d.mesh.mesh import Mesh
from building3d.mesh.quality import minimum_tetra_volume
from building3d.mesh.quality import minimum_triangle_area


def test_mesh_l_shape(show=False):
    stretch = [2.5, 2.5, 2.5]
    p0 = Point(0.0, 0.0, 0.0) * stretch
    p1 = Point(3.0, 0.0, 0.0) * stretch
    p2 = Point(3.0, 2.0, 0.0) * stretch
    p3 = Point(2.0, 2.0, 0.0) * stretch
    p4 = Point(2.0, 1.0, 0.0) * stretch
    p5 = Point(0.0, 1.0, 0.0) * stretch
    p6 = Point(0.0, 0.0, 1.0) * stretch
    p7 = Point(3.0, 0.0, 1.0) * stretch
    p8 = Point(3.0, 2.0, 1.0) * stretch
    p9 = Point(2.0, 2.0, 1.0) * stretch
    p10 = Point(2.0, 1.0, 1.0) * stretch
    p11 = Point(0.0, 1.0, 1.0) * stretch

    floor = Polygon(random_id(), [p0, p5, p4, p3, p2, p1])
    roof = Polygon(random_id(), [p6, p7, p8, p9, p10, p11])
    w_0_1_7_6 = Polygon(random_id(), [p0, p1, p7, p6])
    w_1_2_8_7 = Polygon(random_id(), [p1, p2, p8, p7])
    w_2_3_9_8 = Polygon(random_id(), [p2, p3, p9, p8])
    w_4_10_9_3 = Polygon(random_id(), [p4, p10, p9, p3])
    w_4_5_11_10 = Polygon(random_id(), [p4, p5, p11, p10])
    w_0_6_11_5 = Polygon(random_id(), [p0, p6, p11, p5])

    zone = Solid(
        random_id(),
        [
            floor,
            roof,
            w_0_1_7_6,
            w_1_2_8_7,
            w_2_3_9_8,
            w_4_10_9_3,
            w_4_5_11_10,
            w_0_6_11_5,
        ],
    )
    delta = 1.0

    mesh = Mesh(delta)
    mesh.add_polygon(floor)
    mesh.add_polygon(w_0_1_7_6)
    mesh.add_polygon(w_1_2_8_7)
    mesh.add_polygon(w_2_3_9_8)
    mesh.add_polygon(w_4_10_9_3)
    mesh.add_polygon(w_4_5_11_10)
    mesh.add_polygon(w_0_6_11_5)
    mesh.add_polygon(roof)
    mesh.add_solid(zone)
    mesh.generate()

    solidmesh_stats = mesh.solidmesh.mesh_statistics()
    assert solidmesh_stats["min_element_volume"] > minimum_tetra_volume(
        delta
    ), f"{solidmesh_stats['min_element_volume']=} > {minimum_tetra_volume(delta)=}"

    polymesh_stats = mesh.polymesh.mesh_statistics()
    assert polymesh_stats["min_face_area"] > minimum_triangle_area(
        delta
    ), f"{polymesh_stats['min_face_area']=} > {minimum_triangle_area(delta)=}"

    for el in mesh.solidmesh.elements:
        el_ctr = tetrahedron_centroid(
            p0=mesh.solidmesh.vertices[el[0]],
            p1=mesh.solidmesh.vertices[el[1]],
            p2=mesh.solidmesh.vertices[el[2]],
            p3=mesh.solidmesh.vertices[el[3]],
        )
        assert zone.is_point_inside(el_ctr), "SolidMesh element is outside the solid"

    if show is True:
        mesh.polymesh.mesh_statistics(show=True)
        mesh.solidmesh.mesh_statistics(show=True)
        plot_mesh(mesh, boundary=True, interior=True, show=True)


if __name__ == "__main__":
    test_mesh_l_shape(show=True)
