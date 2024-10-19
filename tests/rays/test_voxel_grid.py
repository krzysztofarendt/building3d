import pytest

from building3d.geom.solid.box import box
from building3d.sim.rays.voxel_grid import make_voxel_grid


def test_voxel_grid_large_step():
    s0 = box(1, 1, 1, (0, 0, 0), name="s0")
    s1 = box(1, 1, 1, (1, 0, 0), name="s1")
    min_xyz = (0.0, 0.0, 0.0)
    max_xyz = (2.0, 1.0, 1.0)
    step = 2.0

    wall_poly_names = [
        ("floor", "floor"),
        ("wall_0", "poly_0"),
        ("wall_1", "poly_1"),
        ("wall_2", "poly_2"),
        ("wall_3", "poly_3"),
        ("ceiling", "ceiling"),
    ]

    poly_pts = []

    for wname, pname in wall_poly_names:
        poly_pts.append(s0[wname][pname].pts)
        poly_pts.append(s1[wname][pname].pts)

    grid = make_voxel_grid(min_xyz, max_xyz, poly_pts, step)

    assert len(grid[(0, 0, 0)]) == 12  # All polygons in this voxel
    assert len(grid[(-1, 0, 0)]) == 5  # 1 front face + 4 perpendicular


def test_voxel_grid_small_step():
    s0 = box(1, 1, 1, (0, 0, 0), name="s0")
    s1 = box(1, 1, 1, (1, 0, 0), name="s1")
    min_xyz = (0.0, 0.0, 0.0)
    max_xyz = (3.0, 1.0, 1.0)
    step = 0.2

    wall_poly_names = [
        ("floor", "floor"),
        ("wall_0", "poly_0"),
        ("wall_1", "poly_1"),
        ("wall_2", "poly_2"),
        ("wall_3", "poly_3"),
        ("ceiling", "ceiling"),
    ]

    poly_pts = []

    for wname, pname in wall_poly_names:
        poly_pts.append(s0[wname][pname].pts)
        poly_pts.append(s1[wname][pname].pts)

    grid = make_voxel_grid(min_xyz, max_xyz, poly_pts, step)

    polygons = set()
    empty_cells = 0
    for val in grid.values():
        for p in val:
            polygons.add(p)
        if len(val) == 0:
            empty_cells += 1

    assert len(polygons) == 12  # All polygons in the grid
    assert empty_cells > 0  # Some cells should have no polygons


def test_voxel_grid_empty():
    s0 = box(1, 1, 1, (0, 0, 0), name="s0")
    s1 = box(1, 1, 1, (1, 0, 0), name="s1")
    min_xyz = (-2.0, -2.0, -2.0)
    max_xyz = (-1.0, -1.0, -1.0)
    step = 0.3

    wall_poly_names = [
        ("floor", "floor"),
        ("wall_0", "poly_0"),
        ("wall_1", "poly_1"),
        ("wall_2", "poly_2"),
        ("wall_3", "poly_3"),
        ("ceiling", "ceiling"),
    ]

    poly_pts = []

    for wname, pname in wall_poly_names:
        poly_pts.append(s0[wname][pname].pts)
        poly_pts.append(s1[wname][pname].pts)

    with pytest.raises(ValueError):
        _ = make_voxel_grid(min_xyz, max_xyz, poly_pts, step)
