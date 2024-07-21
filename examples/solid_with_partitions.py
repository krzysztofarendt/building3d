from building3d.geom.predefined.solids.box import box
from building3d.geom.predefined.walls.partition_plan import partition_plan
from building3d.display.plot_objects import plot_objects


if __name__ == "__main__":
    room = box(7, 5, 3)
    part_1 = partition_plan(
        plan = [(2, 0), (2, 3), (3, 3)],
        height = 3,
    )
    part_2 = partition_plan(
        plan = [(4, 3), (7, 3)],
        height = 3,
    )
    part_3 = partition_plan(
        plan = [(3, 3), (4, 3)],
        height = 1,
        translate = (0, 0, 2),
    )
    objects = [room] + part_1 + part_2 + part_3
    plot_objects(tuple(objects))
