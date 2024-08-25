from building3d.geom.predefined.walls.partition_plan import partition_plan
from building3d.geom.wall import Wall


def test_partition_plan():
    plan = [(0, 0), (5, 0), (5, 5), (10, 5)]
    walls = partition_plan(
        plan=plan,
        height=2.5,
        translate=(0.0, 0.0, 0.0),
        rot_angle=0.0,
    )
    assert len(walls) == len(plan) - 1
    for w in walls:
        assert isinstance(w, Wall)
