from building3d.geom.predefined.walls.partition_plan import partition_plan
from building3d.display.plot_objects import plot_objects


if __name__ == "__main__":
    walls = partition_plan(
        plan=[(0, 0), (5, 0), (5, 5), (10, 5)],
        height=2.5,
        translate=(0.0, 0.0, 0.0),
        rot_angle=0.0,
    )
    plot_objects(tuple(walls))
