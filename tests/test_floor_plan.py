import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.predefined.floor_plan import floor_plan
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.solid import Solid


def test_floor_plan(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    h = 2
    zone = floor_plan(plan, height=h)
    vol = list(zone.get_solids())[0].volume
    assert np.isclose(vol, 5 * 5 * 2)

    walls = zone.get_walls()

    # Make sure normals are pointing outside the zone
    for w in walls:
        wall_normal = w.get_polygons()[0].normal
        if w.name == "wall-0":  # (x=0, y=0) -> (x=5, y=0)
            expected_normal = [0, -1, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "wall-1":  # (x=5, y=0) -> (x=5, y=5)
            expected_normal = [1, 0, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "wall-2":  # (x=5, y=5) -> (x=0, y=5)
            expected_normal = [0, 1, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "wall-3":  # (x=0, y=5) -> (x=0, y=0)
            expected_normal = [-1, 0, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "floor":
            expected_normal = [0, 0, -1]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "ceiling":
            expected_normal = [0, 0, 1]
            assert np.isclose(wall_normal, expected_normal).all()
        else:
            raise ValueError(
                f"This test is using hardcoded wall names. Received name: {w.name}"
            )

    if show:
        plot_objects(*walls)


def test_floor_plan_reversed(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    plan = plan[::-1]
    h = 2
    zone = floor_plan(plan, height=h)
    vol = list(zone.get_solids())[0].volume
    assert np.isclose(vol, 5 * 5 * 2)

    walls = zone.get_walls()

    # Make sure normals are pointing outside the zone
    for w in walls:
        wall_normal = w.get_polygons()[0].normal
        if w.name == "wall-0":  # (x=0, y=5) -> (x=5, y=5)
            expected_normal = [0, 1, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "wall-1":  # (x=5, y=5) -> (x=5, y=0)
            expected_normal = [1, 0, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "wall-2":  # (x=5, y=0) -> (x=0, y=0)
            expected_normal = [0, -1, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "wall-3":  # (x=0, y=0) -> (x=0, y=5)
            expected_normal = [-1, 0, 0]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "floor":
            expected_normal = [0, 0, -1]
            assert np.isclose(wall_normal, expected_normal).all()
        elif w.name == "ceiling":
            expected_normal = [0, 0, 1]
            assert np.isclose(wall_normal, expected_normal).all()
        else:
            raise ValueError(
                f"This test is using hardcoded wall names. Received name: {w.name}"
            )

    if show:
        plot_objects(*walls)


def test_floor_plan_rotated(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    h = 1
    zone = floor_plan(
        plan,
        height = h,
        rot_angle = np.pi / 4,
    )

    vol = list(zone.get_solids())[0].volume
    assert np.isclose(vol, 5 * 5 * 1)

    if show:
        plot_objects(zone)


def test_floor_plan_translated(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    h = 3
    zone = floor_plan(
        plan,
        height = h,
        translate = (10, 10, 10),
    )

    vertices, _ = zone.get_mesh()
    for v in vertices:
        assert v.x > 9.99 and v.y > 9.99 and v.z > 9.99

    vol = list(zone.get_solids())[0].volume
    assert np.isclose(vol, 5 * 5 * 3)

    if show:
        plot_objects(zone)


def test_floor_plan_rotated_and_translated(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    h = 1
    zone = floor_plan(
        plan,
        height = h,
        translate = (10, 10, 10),
        rot_angle = np.pi / 4,
    )

    vol = list(zone.get_solids())[0].volume
    assert np.isclose(vol, 5 * 5 * 1)

    if show:
        plot_objects(zone)


def test_floor_plan_with_apertures(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    h = 1
    apertures = {
        "window-0": ("w0", 0.5, 0.3, 0.3, 0.5),
        "window-1a": ("w1", 0.3, 0.0, 0.1, 0.8),
        "window-1b": ("w1", 0.7, 0.2, 0.2, 0.6),
        "window-2": ("w2", 0.5, 0.3, 0.8, 0.5),
    }

    zone = floor_plan(
        plan,
        height = h,
        name = "room",
        wall_names = ["w0", "w1", "w2", "w3"],
        floor_name = "floor",
        ceiling_name = "ceiling",
        apertures = apertures,
    )

    vol = list(zone.get_solids())[0].volume
    assert np.isclose(vol, 5 * 5 * 1)

    obj = zone.get_object("room")
    assert type(obj) is Solid
    obj = zone.get_object("room/w0")
    assert type(obj) is Wall
    obj = zone.get_object("room/w0/window-0")
    assert type(obj) is Polygon
    obj = zone.get_object("room/w1/window-1a")
    assert type(obj) is Polygon
    obj = zone.get_object("room/w1/window-1b")
    assert type(obj) is Polygon
    obj = zone.get_object("room/w2/window-2")
    assert type(obj) is Polygon

    if show:
        plot_objects(zone)


if __name__ == "__main__":
    # test_floor_plan(show=True)
    # test_floor_plan_reversed(show=True)
    # test_floor_plan_rotated(show=True)
    # test_floor_plan_translated(show=True)
    # test_floor_plan_rotated_and_translated(show=True)
    test_floor_plan_with_apertures(show=True)
