from building3d.geom.point import Point


def are_points_in_set(pts: list[Point], are_in: list[Point]):
    pts_set = set(pts)
    are_in_set = set(are_in)
    return pts_set.issubset(are_in_set)
