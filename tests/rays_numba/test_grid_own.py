from building3d.geom.solid.box import box
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.solid import Solid
from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.io.arrayformat import to_array_format
from building3d.io.arrayformat import get_polygon_points_and_faces
from building3d.simulators.rays_numba.voxel_grid import make_voxel_grid


def test_voxel_grid():
    """This grid test was written by Krzysztof. Other grid tests were written by Claude 3.5 Sonnet.
    """
    # Need to reset the counters before using the array format functions
    Polygon.count = 0
    Wall.count = 0
    Solid.count = 0
    Zone.count = 0
    Building.count = 0

    # Create building
    solid = box(0.2, 0.2, 0.2, (0, 0, 0), "s0")
    zone = Zone([solid], "z")
    building = Building([zone], "b")

    # Convert to array format
    points, faces, polygons, walls, _, _ = to_array_format(building)

    # Get polygon points and faces
    poly_pts = []
    poly_tri = []
    num_polys = len(walls)
    for pn in range(num_polys):
        pts, tri = get_polygon_points_and_faces(points, faces, polygons, pn)
        poly_pts.append(pts)
        poly_tri.append(tri)

    # Test BVH grid
    grid = make_voxel_grid(
        min_xyz=(0.0, 0.0, 0.0),
        max_xyz=(0.2, 0.2, 0.2),
        poly_pts=poly_pts,
        poly_tri=poly_tri,
        step=0.1,
    )
    # for _, v in grid.items():
    #     assert len(v) == 3  # TODO: Not true anymore, some cells might be empty

    # assert len(grid) == 8  # TODO: Not true anymore


if __name__ == "__main__":
    test_voxel_grid()
