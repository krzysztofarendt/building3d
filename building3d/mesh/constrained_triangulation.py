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


def constr_delaunay_triangulation(
    poly: polygon.Polygon,
    delta: float = MESH_DELTA,
    suggest_vertices: list[Point] = [],
    fix_vertices: list[Point] = [],
) -> tuple[list[Point], list[list[int]]]:

    min_area = minimum_triangle_area(delta)

    # Rotate polygon to XY
    logger.debug("Rotating polygon to XY")
    origin = Point(0.0, 0.0, 0.0)
    normal_xy = np.array([0.0, 0.0, 1.0])
    points_xy, rotaxis, phi = rotate_points_to_plane(
        poly.points,
        anchor=origin,
        u=normal_xy,
    )

    z = points_xy[0].z
    points_2d = [Point(p.x, p.y, z) for p in points_xy]

    # Create a 2D polygon instance (used for checking if a point lies inside it)
    poly_2d = polygon.Polygon(random_id(), points_2d)

    # Rotate fixed and suggested points to XY
    fixed_2d, _ = rotate_points_around_vector(fix_vertices, rotaxis, phi)
    suggest_2d, _ = rotate_points_around_vector(suggest_vertices, rotaxis, phi)

    # Add new points on the edges
    logger.debug("Adding new points on the edges of the polygon")
    edge_points = []
    for i in range(len(points_2d)):
        cur = i
        nxt = i + 1 if i + 1 < len(points_2d) else 0
        pt1 = points_2d[cur]
        pt2 = points_2d[nxt]
        edge_len = length(pt2.vector() - pt1.vector())
        num_segments = int(edge_len // (delta + GEOM_EPSILON))
        new_pts = create_points_between_2_points(pt1, pt2, num_segments)
        for p in new_pts:
            is_far_from_all = True
            for fp in fixed_2d:
                dist = length(p.vector() - fp.vector())
                if dist < delta:
                    is_far_from_all = False
                    break
            if is_far_from_all:
                edge_points.append(p)

    points_2d.extend(edge_points)

    # Add new points inside the polygon
    logger.debug("Adding new points inside the polygon")

    xaxis = [p.x for p in points_2d]
    yaxis = [p.y for p in points_2d]
    xmin, xmax = min(xaxis), max(xaxis)
    ymin, ymax = min(yaxis), max(yaxis)

    xgrid = np.arange(xmin + delta, xmax, delta)
    ygrid = np.arange(ymin + delta, ymax, delta)
    for x in xgrid:
        for y in ygrid:
            p = Point(
                x + random_within(MESH_JOGGLE),
                y + random_within(MESH_JOGGLE),
                z,
            )
            is_far_from_all = True
            for fp in fixed_2d:
                dist = length(p.vector() - fp.vector())
                if dist < delta / 3.0:  # TODO: Add to config
                    is_far_from_all = False
                    break
            if is_far_from_all:
                if poly_2d.is_point_inside_margin(p, margin=delta/2):
                    points_2d.append(p)

    # Add polygon points to fixed and suggested
    points_2d.extend(fixed_2d)
    points_2d.extend(suggest_2d)

    # Triangulation - first pass
    logger.debug("Triangulation - first pass")

    pts_arr = np.array([[p.x, p.y] for p in points_2d])
    tri = Delaunay(pts_arr, incremental=False)
    triangles = tri.simplices

    logger.debug(f"{len(triangles)=}")

    # DONE: Below removal must take into account fixed points
    # TODO: If done once, this can lead to uneven distribution of points
    # TODO: It should be iterative and adaptive
    # Remove points not used in the triangulation
    # and remove small faces
    unique_tri_indices = np.unique(triangles)
    final_points_2d = []

    pt_to_area = {}
    for t in triangles:
        p0, p1, p2 = points_2d[t[0]], points_2d[t[1]], points_2d[t[2]]
        area = triangle_area(p0, p1, p2)
        for i in range(3):
            if t[i] not in pt_to_area:
                pt_to_area[t[i]] = area
            elif area < pt_to_area[t[i]]:
                pt_to_area[t[i]] = area

    for i, p in enumerate(points_2d):
        if i in unique_tri_indices:
            if pt_to_area[i] > min_area or points_2d[i] in fixed_2d:
                final_points_2d.append(p)

    # Triangulation - second pass
    logger.debug("Triangulation - second pass")

    pts_arr = np.array([[p.x, p.y] for p in final_points_2d])
    tri = Delaunay(pts_arr, incremental=False)
    triangles = tri.simplices

    logger.debug(f"{len(triangles)=}")
    assert len(np.unique(triangles)) == len(final_points_2d)
    points_2d = final_points_2d

    faces = triangles.tolist()

    # Manually add fixed points if not present
    # TODO: is it ever the case?
    pass  # TODO

    # Rotate back to 3D
    new_points, _ = rotate_points_around_vector(
        points_2d,
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
        error_msg = \
            f"Mesh face normal points in a different direction ({mesh_normal}) " + \
            f"than polygon normal ({poly.normal})."
        logger.error(error_msg)
        raise GeometryError(error_msg)

    del poly_2d
    return new_points, faces
