import numpy as np

from building3d.geom.predefined.floor_plan import floor_plan
from building3d.display.plot_objects import plot_objects


def test_floor_plan(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    h = 2
    zone = floor_plan(plan, height=h)
    vol = list(zone.solids.values())[0].volume
    assert np.isclose(vol, 5 * 5 * 2)

    wall_names = zone.get_wall_list()
    walls = [zone.get_wall(name) for name in wall_names]

    # TODO: Make sure normals are pointing outside the zone

    if show:
        plot_objects(*walls)


def test_floor_plan_reversed(show=False):
    plan = [(0, 0), (5, 0), (5, 5), (0, 5)]
    plan = plan[::-1]
    h = 2
    zone = floor_plan(plan, height=h)
    vol = list(zone.solids.values())[0].volume
    assert np.isclose(vol, 5 * 5 * 2)

    wall_names = zone.get_wall_list()
    walls = [zone.get_wall(name) for name in wall_names]

    # TODO: Make sure normals are pointing outside the zone

    if show:
        plot_objects(*walls)


if __name__ == "__main__":
    test_floor_plan(show=True)
    test_floor_plan_reversed(show=True)
