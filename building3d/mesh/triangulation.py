from __future__ import annotations  # Needed for type hints to work (due to circular import)
import logging

import numpy as np
from scipy.spatial import Delaunay

import building3d.geom.polygon as polygon  # Needed to break circular import
from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.rotate import rotate_points_to_plane
from building3d.geom.rotate import rotate_points_around_vector
from building3d.geom.vector import length
from building3d.geom.vector import normal
from building3d.geom.line import create_points_between_2_points
from building3d.geom.triangle import triangle_area
from building3d.geom.triangle import triangle_centroid
from building3d.geom.triangle import minimum_triangle_area
from building3d import random_id
from building3d.mesh.exceptions import MeshError
from building3d.config import GEOM_EPSILON
from building3d.config import MESH_JOGGLE
from building3d.config import MESH_DELTA
from building3d import random_within


logger = logging.getLogger(__name__)


def delaunay_triangulation(
    poly: polygon.Polygon,
    delta: float = MESH_DELTA,
    init_vertices: list[Point] = [],
) -> tuple[list[Point], list[list[int]]]:
    """Delaunay triangulation of a polygon.

    Steps:
      - rotate points to plane XY
      - add points in 2D
      - run triangulation in 2D
      - rotate new points back to the original plane
      - change triangle vertex ordering to match the polygon's surface normal direction

    Args:
        poly: polygon to be meshed
        delta: approximate mesh size
        init_vertices: initial vertices to be used for triangulation

    Return:
        (list of mesh points, list of faces)
    """
    logger.debug(f"Starting triangulation for {poly}")
    logger.debug(f"{delta=}")
    logger.debug(f"{len(init_vertices)=}")

    min_area = minimum_triangle_area(delta)
    logger.debug(f"Choosing min. face area -> {min_area}")

    # Placeholder for points on the edges of the polygon
    edge_pts_2d = []

    # If init_vertices are used, make sure they contain enough points
    if len(init_vertices) > 0:
        for p in poly.points:
            if p not in init_vertices:
                error_msg = "Missing polygon vertex in init_vertices"
                logger.error(error_msg)
                raise MeshError(error_msg)
        if len(init_vertices) == len(poly.points):
            error_msg = "Init_vertices contains only polygon vertices! That's not enough."
            logger.error(error_msg)
            raise MeshError(error_msg)

    # Rotate polygon points to XY
    logger.debug("Rotating polygon to XY")
    origin = Point(0.0, 0.0, 0.0)
    normal_xy = np.array([0.0, 0.0, 1.0])
    points_xy, rotaxis, phi = rotate_points_to_plane(
        poly.points,
        anchor=origin,
        u=normal_xy,
    )

    z = points_xy[0].z
    new_points_2d = [Point(p.x, p.y, z) for p in points_xy]
    logger.debug(f"{len(new_points_2d)=}")
    logger.debug(f"new_points_2d = [{new_points_2d[0], new_points_2d[1]}, ..., {new_points_2d[-1]}]")

    # Create a 2D polygon instance (used for checking if a point lies inside it)
    poly_2d = polygon.Polygon(random_id(), new_points_2d)

    if init_vertices is not None and len(init_vertices) > 0:
        # Rotate initial vertices to XY
        logger.debug("Rotating initial vertices to XY")

        init_vertices_xy, _ = rotate_points_around_vector(init_vertices, rotaxis, phi)
        new_points_2d.extend(init_vertices_xy)
    else:
        # Add new points on the edges
        logger.debug("Adding new points on the edges")

        for i in range(len(new_points_2d)):
            cur = i
            nxt = i + 1 if i + 1 < len(new_points_2d) else 0
            pt1 = new_points_2d[cur]
            pt2 = new_points_2d[nxt]
            logger.debug(f"Edge between points {pt1} and {pt2}")
            edge_len = length(pt2.vector() - pt1.vector())
            num_segments = int(edge_len // (delta + GEOM_EPSILON))
            new_pts = create_points_between_2_points(pt1, pt2, num_segments)
            edge_pts_2d.extend(new_pts)

        new_points_2d.extend(edge_pts_2d)

        # Add new points inside the polygon
        logger.debug("Adding new points inside the polygon")

        xaxis = [p.x for p in new_points_2d]
        yaxis = [p.y for p in new_points_2d]
        xmin, xmax = min(xaxis), max(xaxis)
        ymin, ymax = min(yaxis), max(yaxis)

        xgrid = np.arange(xmin + delta, xmax, delta)
        ygrid = np.arange(ymin + delta, ymax, delta)
        for x in xgrid:
            for y in ygrid:
                pt = Point(
                    x + random_within(MESH_JOGGLE),
                    y + random_within(MESH_JOGGLE),
                    z,
                )
                if poly_2d.is_point_inside_margin(pt, margin=delta/2):
                    new_points_2d.append(pt)

    # Triangulation - first pass
    logger.debug("Triangulation - first pass")

    pts_arr = np.array([[p.x, p.y] for p in new_points_2d])
    tri = Delaunay(pts_arr, incremental=False)
    triangles = tri.simplices

    logger.debug(f"{len(triangles)=}")

    # Remove points not used in the triangulation
    # and remove small faces
    unique_tri_indices = np.unique(triangles)
    final_points_2d = []

    pt_to_area = {}
    for t in triangles:
        p0, p1, p2 = new_points_2d[t[0]], new_points_2d[t[1]], new_points_2d[t[2]]
        area = triangle_area(p0, p1, p2)
        for i in range(3):
            if t[i] not in pt_to_area:
                pt_to_area[t[i]] = area
            elif area < pt_to_area[t[i]]:
                pt_to_area[t[i]] = area

    for i, p in enumerate(new_points_2d):
        if i in unique_tri_indices:
            if pt_to_area[i] > min_area or new_points_2d[i] in edge_pts_2d:
                final_points_2d.append(p)

    # Triangulation - second pass
    logger.debug("Triangulation - second pass")

    pts_arr = np.array([[p.x, p.y] for p in final_points_2d])
    tri = Delaunay(pts_arr, incremental=False)
    triangles = tri.simplices
    convex_hull = np.unique(tri.convex_hull).tolist()

    logger.debug(f"{len(triangles)=}")
    assert len(np.unique(triangles)) == len(final_points_2d)

    faces = triangles.tolist()

    # Rotate back to 3D
    new_points, _ = rotate_points_around_vector(
        final_points_2d,
        u=rotaxis,
        phi=-phi,
    )

    # Delete faces which are outside the polygon (non-convex polygons)
    faces_to_keep = []
    for i, f in enumerate(faces):
        p0 = new_points[f[0]]
        p1 = new_points[f[1]]
        p2 = new_points[f[2]]
        c = triangle_centroid(p0, p1, p2)
        if poly.is_point_inside(c):
            faces_to_keep.append(f)
        else:
            logger.warning(
                f"Face {i} (vertex indices {f}, centroid {c}) is outside {poly} "
                "and will be removed"
            )
    faces = faces_to_keep

    # edge_pts, _ = rotate_points_around_vector(
    #     edge_pts_2d,
    #     u=rotaxis,
    #     phi=-phi,
    # )

    # Fix surface normal direction
    def face_normal(face_num):
        p0 = new_points[faces[face_num][0]]
        p1 = new_points[faces[face_num][1]]
        p2 = new_points[faces[face_num][2]]
        return normal(p0, p1, p2)

    logger.debug(f"{poly.normal=}")

    for face_num in range(len(faces)):
        face_n = face_normal(face_num)
        if np.isclose(face_n * -1., poly.normal).all():
            logger.debug(f"Reordering face no. {face_num} vertices to flip the normal vector")
            faces[face_num] = [faces[face_num][0], faces[face_num][2], faces[face_num][1]]

    mesh_normal = face_normal(0)

    if np.isclose(mesh_normal, poly.normal, atol=GEOM_EPSILON).all():
        # Vertex ordering is correct
        pass
    else:
        error_msg = f"Mesh face normal points in a different direction ({mesh_normal}) " + \
            f"than polygon normal ({poly.normal}). " + \
            "This should never happen."
        logger.error(error_msg)
        raise GeometryError(error_msg)

    del poly_2d
    return new_points, faces

