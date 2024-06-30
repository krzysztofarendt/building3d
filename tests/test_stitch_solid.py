import pytest

import numpy as np

from building3d.geom.exceptions import GeometryError
from building3d.geom.predefined.solids.box import box
from building3d.geom.operations.stitch_solids import stitch_solids


def test_stitch_solids_same_size():
    b1 = box(1, 1, 1, name="b1")
    b2 = box(1, 1, 1, (1, 0, 0), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

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

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) < len(b2_new.get_polygons())


def test_stitch_solids_overlapping_2():
    # TODO: This case does not work, because 1 edge is coincident
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
    # TODO: This case does not work, because 2 edges are coincident
    b1 = box(1, 1, 1, name="b1")
    b2 = box(1, 1, 1, (1, 0.5, 0.0), name="b2")
    b1_new, b2_new = stitch_solids(b1, b2)

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

    assert b1.name == b1_new.name
    assert b1.uid == b1_new.uid
    assert np.isclose(b1.volume, b1_new.volume)
    assert len(b1.get_polygons()) < len(b1_new.get_polygons())

    assert b2.name == b2_new.name
    assert b2.uid == b2_new.uid
    assert np.isclose(b2.volume, b2_new.volume)
    assert len(b2.get_polygons()) < len(b2_new.get_polygons())


if __name__ == "__main__":
    test_stitch_solids_overlapping_3()
