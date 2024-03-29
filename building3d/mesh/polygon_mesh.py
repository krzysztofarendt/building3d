import numpy as np
from scipy.spatial import Delaunay

from ..geom.polygon import Polygon
from ..geom.point import Point
from ..geom.rotate import rotate_points_to_plane
from ..geom.rotate import rotate_points
from ..geom.rotate import rotate_points_around_vector
from ..geom.vector import length
from ..geom.vector import normal
from ..geom.line import create_points_between_2_points


def delaunay_triangulation(points: list[Point], centroid: Point) -> tuple[list[Point], list[int]]:

    normal_original = normal(points[0], points[1], points[2])

    # Steps:
    #   - rotate points to plane XY
    #   - add points in 2D
    #   - run triangulation in 2D
    #   - rotate new points back to the original plane

    # Rotate points to XY
    origin = Point(0.0, 0.0, 0.0)
    normal_xy = np.array([0.0, 0.0, 1.0])
    points_xy, R = rotate_points_to_plane(
        points,
        anchor=centroid,
        u=normal_xy,
        d=0.0,
    )

    z = points_xy[0].z
    new_points_2d = [Point(p.x, p.y, z) for p in points_xy]
    poly_2d = Polygon(new_points_2d)

    # Mesh size
    delta = 0.5

    # Add new points on the edges
    edge_pts_2d = []
    for i in range(len(new_points_2d)):
        cur = i
        nxt = i + 1 if i + 1 < len(new_points_2d) else 0
        pt1 = new_points_2d[cur]
        pt2 = new_points_2d[nxt]

        edge_len = length(pt2.vector() - pt1.vector())
        num_segments = int(edge_len // delta)
        new_pts = create_points_between_2_points(pt1, pt2, num_segments)
        edge_pts_2d.extend(new_pts)

    new_points_2d.extend(edge_pts_2d)

    # Add new points inside the polygon
    xaxis = [p.x for p in new_points_2d]
    yaxis = [p.y for p in new_points_2d]
    xmin, xmax = min(xaxis), max(xaxis)
    ymin, ymax = min(yaxis), max(yaxis)

    xgrid = np.arange(xmin, xmax, delta)
    ygrid = np.arange(ymin, ymax, delta)
    for x in xgrid:
        for y in ygrid:
            pt = Point(x, y, z)
            if poly_2d.is_point_inside(pt):
                new_points_2d.append(Point(x, y, z))

    pts_arr = np.array([[p.x, p.y] for p in new_points_2d])
    tri = Delaunay(pts_arr, incremental=True)
    triangles = tri.simplices

    # Remove points not used in the triangulation and rerun triangulation
    unique_tri_indices = np.unique(triangles)
    final_points_2d = []
    for i, p in enumerate(new_points_2d):
        if i in unique_tri_indices:
            final_points_2d.append(p)

    # TODO: Inefficient code, using Delaunay twice!
    pts_arr = np.array([[p.x, p.y] for p in final_points_2d])
    tri = Delaunay(pts_arr, incremental=True)
    triangles = tri.simplices
    assert len(np.unique(triangles)) == len(final_points_2d)

    # Rotate back to 3D
    # TODO: Mostly does not work
    new_points, _ = rotate_points_to_plane(
        final_points_2d,
        anchor=centroid,
        u=normal_original,
        d=0.0,
    )

    return new_points, triangles.tolist()

