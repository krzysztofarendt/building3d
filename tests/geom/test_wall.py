import numpy as np

from building3d.random import random_id
from building3d.geom.points import new_point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall


def test_wall_single():
    pts0 = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [2.0, 1.0, 0.0],
            [2.0, 2.0, 0.0],
            [1.0, 2.0, 0.0],
            [1.0, 3.0, 0.0],
            [0.0, 3.0, 0.0],
        ]
    )
    poly0 = Polygon(pts0, name="poly0")
    wall = Wall([poly0])
    assert list(wall.children.values())[0] is poly0
    assert wall["poly0"] is poly0

    name = "wall"
    wall = Wall([poly0], name="wall")
    assert wall.name == name
    assert list(wall.children.values())[0] is poly0

    uid = random_id()
    wall = Wall([poly0], name="wall", uid=uid)
    assert wall.name == name
    assert wall.uid == uid
    assert list(wall.children.values())[0] is poly0

    wall = Wall()
    wall.add_polygon(poly0)
    assert list(wall.children.values())[0] is poly0

    verts, faces = wall.get_mesh()
    assert np.allclose(verts, pts0)
    assert np.allclose(faces, poly0.tri)


def test_wall_double():
    pts0 = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [2.0, 1.0, 0.0],
            [2.0, 2.0, 0.0],
            [1.0, 2.0, 0.0],
            [1.0, 3.0, 0.0],
            [0.0, 3.0, 0.0],
        ]
    )
    poly0 = Polygon(pts0, name="poly0")

    pts1 = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
        ]
    )
    poly1 = Polygon(pts1, name="poly1")

    wall = Wall([poly0, poly1], name="wall")
    assert wall.name == "wall"
    assert list(wall.children.values())[0] is poly0
    assert list(wall.children.values())[1] is poly1
    assert list(wall.children.keys()) == ["poly0", "poly1"]
    assert isinstance(wall["poly0"], Polygon)
    assert wall["poly0"] is poly0
    assert wall["poly1"] is poly1


def test_wall_bbox():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    poly = Polygon(pts, name="poly")
    wall = Wall([poly])
    bbox = wall.bbox()
    assert np.allclose(bbox[0], [0, 0, 0])
    assert np.allclose(bbox[1], [1, 1, 0])
