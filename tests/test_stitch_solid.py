import numpy as np
import pytest

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.exceptions import GeometryError
from building3d.geom.operations.stitch_solids import stitch_solids
from building3d.geom.predefined.solids.box import box


def test_stitch_solids_same_size():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(1, 1, 1, (1, 0, 0), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert len(b1.get_polygons()) == len(b2.get_polygons())
    assert len(b1_new.get_polygons()) == len(b2_new.get_polygons())

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)

    assert b1 is b1_new
    assert b2 is b2_new


def test_stitch_solids_same_size_not_touching():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(1, 1, 1, (2, 0, 0), name="b2")
    with pytest.raises(GeometryError):
        _, _ = stitch_solids(b1, b2)


def test_stitch_solids_diff_sizes_vertices_and_edges_not_touching():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(0.5, 0.5, 0.5, (1, 0.25, 0.25), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)


def test_stitch_solids_diff_sizes_edge_touching():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(0.5, 0.5, 0.5, (1, 0.25, 0), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)


def test_stitch_solids_diff_sizes_2_corners():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(1, 1, 0.1, (1, 0, 0), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)


def test_stitch_solids_diff_sizes_vertices_touching():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(0.5, 0.5, 0.5, (1, 0, 0), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)

    b1 = box(0.5, 0.5, 0.5, (1, 0, 0), name="b1")
    b2 = box(1, 1, 1, name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) < len(b2_new.get_polygons())


def test_stitch_solids_diff_sizes_vertices_one_inside_the_other():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(0.5, 0.5, 0.5, (0, 0, 0), name="b2")
    with pytest.raises(GeometryError):
        _, _ = stitch_solids(b1, b2)


def test_stitch_solids_overlapping_1():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(1, 1, 1, (1, 0.5, 0.5), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert len(b1.get_polygons()) == len(b2.get_polygons())
    assert len(b1_new.get_polygons()) == len(b2_new.get_polygons())

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) < len(b2_new.get_polygons())


def test_stitch_solids_overlapping_2():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(0.5, 0.5, 0.5, (1, 0.5, 0.25), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) == len(b2_new.get_polygons())


def test_stitch_solids_overlapping_3():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(1, 1, 1, (1, 0.5, 0.0), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert len(b1.get_polygons()) == len(b2.get_polygons())
    assert len(b1_new.get_polygons()) == len(b2_new.get_polygons())

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) < len(b2_new.get_polygons())


def test_stitch_solids_overlapping_4():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(0.5, 0.5, 0.5, (1, 0.75, 0.25), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert len(b1.get_polygons()) == len(b2.get_polygons())
    assert len(b1_new.get_polygons()) == len(b2_new.get_polygons())

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) < len(b2_new.get_polygons())

    # Switch b1 <-> b2
    b1 = box(0.5, 0.5, 0.5, (1, 0.75, 0.25), name="b1")
    b2 = box(1, 1, 1, name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

    assert len(b1.get_polygons()) == len(b2.get_polygons())
    assert len(b1_new.get_polygons()) == len(b2_new.get_polygons())

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) < len(b2_new.get_polygons())


def test_stitch_solids_2_corners_additional_points_in_b1():
    # Create manually a geometry which is equivalent to:
    # b1 = box(1, 1, 1, name="b1")
    # However use more points for the polygon adjacent to b2
    # to check if it still works
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p1b = Point(1.0, 0.5, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall(
        [Polygon([p0, p3, p2, p1b, p1])]
    )  # Additional point must be added here...
    wall0 = Wall([Polygon([p0, p1, p5, p4])])
    poly1 = Polygon([p1, p1b, p2, p6, p5])
    wall1 = Wall([poly1])  # ...and here (Polygon adjacent to b2)
    wall2 = Wall([Polygon([p3, p7, p6, p2])])
    wall3 = Wall([Polygon([p0, p4, p7, p3])])
    ceiling = Wall([Polygon([p4, p5, p6, p7])])

    b1 = Solid([floor, wall0, wall1, wall2, wall3, ceiling], name="b1")
    b2 = box(1, 1, 0.1, (1, 0, 0), name="b2")

    # Original solids should have the same number of polygons (=6)
    assert len(b1.get_polygons()) == len(b2.get_polygons())
    assert len(b1.get_polygons()) == 6

    b1_new, b2_new = stitch_solids(b1, b2)

    # Stitched solids should have different number of polygons
    # b1 is bigger, so 1 new polygon must be added
    assert len(b1_new.get_polygons()) == 7
    assert len(b2_new.get_polygons()) == 6

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)


if __name__ == "__main__":
    test_stitch_solids_2_corners_additional_points_in_b1()
