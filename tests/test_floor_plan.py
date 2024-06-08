from building3d.geom.predefined.floor_plan import floor_plan
from building3d.display.plot_objects import plot_objects


def test_floor_plan():
    plan = [(0, 0), (5, 0), (5, 5), (0, 2.5)]
    h = 2
    zone = floor_plan(plan, height=h)

    wall_names = zone.get_wall_list()
    walls = [zone.get_wall(name) for name in wall_names]

    plot_objects(*walls)


if __name__ == "__main__":
    test_floor_plan()
