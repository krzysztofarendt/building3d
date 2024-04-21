import numpy as np

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.mesh.quality import purge_mesh


def test_purge_mesh(show=False):
    # L-shape
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)

    # Generate some triangles
    poly = Polygon([p0, p1, p2, p3, p4, p5])
    vertices = poly.points
    faces = poly.triangles
    del poly  # Not needed anymore

    if show:
        print("Original mesh:")
        print(vertices)
        print(faces)

    # Remove 1 face
    faces = faces[1:]

    if show:
        print("After removing 1 face:")
        print(vertices)
        print(faces)

    # Purge
    vertices, faces = purge_mesh(vertices, faces)

    if show:
        print("After purging:")
        print(vertices)
        print(faces)

    # Make sure all vertices are present in new mesh
    assert set(np.unique(np.array(faces))) == set([i for i in range(len(vertices))])


if __name__ == "__main__":
    test_purge_mesh(show=True)
