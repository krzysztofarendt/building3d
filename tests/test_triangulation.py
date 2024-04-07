from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.wall import Wall
from building3d.mesh.triangulation import delaunay_triangulation


def test_delaunay_triangulation_init_vertices_with_centroid():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    floor = Wall(random_id(), [p0, p3, p2, p1])
    init_vertices = floor.points + [floor.centroid]
    vertices, faces = delaunay_triangulation(floor, init_vertices=init_vertices)

    assert len(faces) == 4
    assert len(vertices) == 5


def test_delaunay_triangulation_init_vertices_without_polygon_vertex():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    floor = Wall(random_id(), [p0, p3, p2, p1])

    vertices_1, faces_1 = delaunay_triangulation(floor, init_vertices=None)

    # Remove a corner vertex
    vertices_2 = vertices_1[1:]
    excluded_pt_index = 0
    faces_2 = [f for f in faces_1 if excluded_pt_index not in f]

    # Make sure only 1 face was removed due to removing the corner vertex
    assert len(faces_2) == len(faces_1) - 1

    # Run triangulation again but with vertices_2 as initial vertices
    vertices_3, faces_3 = delaunay_triangulation(floor, init_vertices=vertices_2)

    # Make sure vertices_3 == vertices_1, because delaunay_triangulation should add
    # back the corner point, because it is a vertex polygon
    assert vertices_1 == vertices_3
    assert faces_1 == faces_3
