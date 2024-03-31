import numpy as np

from building3d import random_id
from building3d.config import GEOM_EPSILON
from building3d.geom.point import Point
from building3d.geom.vector import normal
from building3d.geom.wall import Wall
from building3d.mesh.mesh import Mesh


def test_collapse_points():
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

    mesh = Mesh()
    mesh.add_polygon(floor)
    mesh.add_polygon(wall0)
    mesh.add_polygon(wall1)
    mesh.add_polygon(wall2)
    mesh.add_polygon(wall3)
    mesh.add_polygon(roof)
    mesh.generate()

    vertices = [v for v in mesh.vertices]
    faces = [f for f in mesh.faces]

    mesh.collapse_points()

    new_vertices = [v for v in mesh.vertices]
    new_faces = [f for f in mesh.faces]

    for v in new_vertices:
        assert v is not None

    max_f = 0
    for f in faces:
        for fv in f:
            if fv > max_f:
                max_f = fv

    max_new_f = 0
    for f in new_faces:
        for fv in f:
            if fv > max_new_f:
                max_new_f = fv

    diff_num_vertices = len(vertices) - len(new_vertices)
    assert max_f - diff_num_vertices == max_new_f

    # Check if face normals are equal for each face attached to a given polygon
    for i, face in enumerate(mesh.faces):
        poly_name = mesh.face_owners[i]
        poly = mesh.polygons[poly_name]
        p0 = mesh.vertices[face[0]]
        p1 = mesh.vertices[face[1]]
        p2 = mesh.vertices[face[2]]
        vnorm = normal(p0, p1, p2)
        assert np.isclose(
            vnorm, poly.normal, atol=GEOM_EPSILON
        ).all()  # TODO: Should be same, but is not


if __name__ == "__main__":
    test_collapse_points()
