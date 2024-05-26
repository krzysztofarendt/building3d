from building3d.display.plot_mesh import plot_mesh
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.triangle import triangle_centroid
from building3d.mesh.polymesh import PolyMesh
from building3d.mesh.triangulation import delaunay_triangulation


def test_constr_triangulation(show=False):
    # Polygon vertices
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)

    poly = Polygon([p0, p1, p2, p3, p4, p5])

    # Fixed vertices
    f0 = Point(0.2, 0.0, 0.0)
    f1 = Point(0.4, 0.0, 0.0)
    f2 = Point(0.6, 0.0, 0.0)
    f3 = Point(0.8, 0.0, 0.0)
    f4 = Point(0.5, 0.5, 0.0)
    f5 = Point(1.0, 0.5, 0.0)
    f6 = Point(1.1, 0.6, 0.0)
    f7 = Point(1.2, 0.7, 0.0)
    fix_points = [f0, f1, f2, f3, f4, f5, f6, f7]

    for delta in [0.075, 0.3, 1.0]:
        # Constrained
        vertices, faces = delaunay_triangulation(
            poly,
            delta=delta,
            fixed_points=fix_points,
        )
        mesh = PolyMesh(delta)
        mesh.vertices = vertices
        mesh.faces = faces
        mesh.polygons = {poly.name: poly}

        # Check if all faces are inside the polygon
        for f in mesh.faces:
            p0 = mesh.vertices[f[0]]
            p1 = mesh.vertices[f[1]]
            p2 = mesh.vertices[f[2]]
            c = triangle_centroid(p0, p1, p2)
            assert poly.is_point_inside(c), "Face outside polygon!"

        # Check if all polygon points are in mesh
        for pt in poly.points:
            assert pt in mesh.vertices, f"Polygon vertex not in mesh: {pt}"

        # Check if all fixed points are in mesh
        for pt in fix_points:
            assert pt in mesh.vertices, f"Fixed point not in mesh: {pt}"

        if show:
            plot_mesh(mesh)


def test_delaunay_triangulation_init_vertices_with_centroid():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    floor = Polygon([p0, p3, p2, p1])
    fixed = floor.points + [floor.centroid]
    vertices, faces = delaunay_triangulation(floor, fixed_points=fixed)

    assert len(faces) == 4
    assert len(vertices) == 5


def test_delaunay_triangulation_init_vertices_without_polygon_vertex():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    floor = Polygon([p0, p3, p2, p1])

    vertices_1, faces_1 = delaunay_triangulation(floor)

    # Remove a corner vertex
    vertices_2 = vertices_1[1:]
    excluded_pt_index = 0
    faces_2 = [f for f in faces_1 if excluded_pt_index not in f]

    # Make sure only 1 face was removed due to removing the corner vertex
    assert len(faces_2) == len(faces_1) - 1

    # Run triangulation again but with vertices_2 as fixed vertices
    # Make sure the missing corner is added back
    vertices_3, faces_3 = delaunay_triangulation(floor, fixed_points=vertices_2)
    assert vertices_1[0] in vertices_3, "Missing corner not added to vertices"
    assert len(faces_3) == len(faces_2) + 1


if __name__ == "__main__":
    test_constr_triangulation(show=True)
